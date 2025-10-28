# communication/views.py
import json
import uuid
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache
from django.contrib import messages
from django.utils import timezone
from io import BytesIO
import logging
from .models import AssistantIA
from .services.ai_service import ai_service

from .models import RapportPDF, ModeleRapport, HistoriqueGeneration, AssistantIA, SuggestionConnexion
from django.db.models import Q
from .services.pdf_generator import PDFGenerationService
from dashboard.models import Statistique
from journal.models import Journal
from recommendations.models import Recommandation, Objectif
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

from django.core import serializers

# ✅ AJOUTER : Vue dashboard pour communication
class DashboardCommunicationView(LoginRequiredMixin, View):
    """Vue principale du tableau de bord communication"""
    
    def get(self, request):
        context = {
            'active_tab': 'communication',
            'rapports_count': RapportPDF.objects.filter(utilisateur=request.user).count(),
            'assistant_messages_count': AssistantIA.objects.filter(utilisateur=request.user).count(),
            'suggestions_count': SuggestionConnexion.objects.filter(utilisateur_source=request.user).count(),
        }
        return render(request, 'communication/dashboard.html', context)

#############################################################################################################################
#############################################################################################################################
# ... PDF views ...

# ✅ UNE SEULE DÉFINITION de ListeRapportsView
class ListeRapportsView(LoginRequiredMixin, View):
    """View to list and manage user's PDF reports"""
    

    def post(self, request):
        """Handle bulk delete requests"""
        if 'delete_selected' in request.POST:
            rapport_ids = request.POST.getlist('selected_reports')
            deleted_count = 0
            
            for rapport_id in rapport_ids:
                try:
                    rapport = RapportPDF.objects.get(id=rapport_id, utilisateur=request.user)
                    rapport.delete()
                    deleted_count += 1
                except RapportPDF.DoesNotExist:
                    continue
            
            if deleted_count > 0:
                messages.success(request, f"✅ {deleted_count} rapport(s) supprimé(s) avec succès")
            else:
                messages.warning(request, "Aucun rapport sélectionné pour la suppression")
        
        return redirect('communication:liste_rapports')
    

    def get(self, request):
        rapports = RapportPDF.objects.filter(
            utilisateur=request.user
        ).select_related('statistique').order_by('-date_generation')
        
        context = {
            'rapports': rapports,
            'active_tab': 'reports',
        }
        return render(request, 'communication/rapports/liste_rapports.html', context)

class GenererRapportPDFView(LoginRequiredMixin, View):
    """View to generate PDF reports"""
    
    def get(self, request):
        """Display report generation form"""
        try:
            # Get available statistics for the user
            statistiques = Statistique.objects.filter(utilisateur=request.user)
            
            if not statistiques.exists():
                messages.warning(request, "Vous n'avez pas encore de statistiques. Veuillez d'abord créer des entrées de journal.")
                return redirect('journal:liste_journaux')
            
            modeles = ModeleRapport.objects.filter(public=True)
            
            context = {
                'modeles': modeles,
                'statistiques': statistiques,
                'formats_rapport': RapportPDF.FORMAT_RAPPORT_CHOICES,
                'templates_rapport': RapportPDF.TEMPLATE_CHOICES,
                'active_tab': 'generate_report',
            }
            return render(request, 'communication/rapports/generer_rapport.html', context)
            
        except Exception as e:
            logger.error(f"Error loading report generation form: {str(e)}")
            messages.error(request, "Erreur lors du chargement du formulaire")
            return redirect('communication:liste_rapports')
    
    def post(self, request):
        """Handle PDF generation request"""
        try:
            data = request.POST
            
            # Get related objects
            statistique_id = data.get('statistique_id')
            if not statistique_id:
                messages.error(request, "Veuillez sélectionner des statistiques")
                return redirect('communication:generer_rapport')
                
            statistique = get_object_or_404(Statistique, id=statistique_id, utilisateur=request.user)
            
            # Check if rapport already exists using filter
            existing_rapport = RapportPDF.objects.filter(statistique=statistique).first()
            if existing_rapport:
                messages.warning(request, f"Un rapport existe déjà pour {statistique.periode}. Vous pouvez le dupliquer ou le regénérer.")
                return redirect('communication:liste_rapports')
            
            # ✅ FIX: Proper boolean handling for checkboxes
            def get_boolean_value(field_name, default=False):
                value = data.get(field_name)
                # Checkboxes return 'on' when checked, None when unchecked
                return value == 'on' if value is not None else default
            
            # Create rapport record with proper boolean values
            rapport = RapportPDF.objects.create(
                utilisateur=request.user,
                statistique=statistique,
                titre=data.get('titre', 'Rapport Mensuel'),
                mois=data.get('mois', statistique.periode),
                format_rapport=data.get('format_rapport', 'complet'),
                template_rapport=data.get('template_rapport', 'moderne'),
                couleur_principale=data.get('couleur_principale', '#3498db'),
                # ✅ FIX: Use the helper function for boolean fields
                inclure_statistiques=get_boolean_value('inclure_statistiques', True),
                inclure_graphiques=get_boolean_value('inclure_graphiques', True),
                inclure_analyse_ia=get_boolean_value('inclure_analyse_ia', True),
                inclure_journaux=get_boolean_value('inclure_journaux', False),
                inclure_objectifs=get_boolean_value('inclure_objectifs', True),
                inclure_recommandations=get_boolean_value('inclure_recommandations', True),
                statut='en_cours'
            )
            
            # Create generation history
            historique = HistoriqueGeneration.objects.create(
                rapport=rapport,
                statut='debute'
            )
            
            # Generate PDF
            pdf_service = PDFGenerationService()
            
            try:
                # Generate PDF content
                pdf_content = pdf_service.generate_complete_report(rapport)
                
                # Save PDF to FileField
                filename = rapport.generer_nom_fichier()
                rapport.contenu_pdf.save(filename, ContentFile(pdf_content))
                
                # Update status
                rapport.statut = 'termine'
                rapport.save()
                
                # Update history
                historique.statut = 'reussi'
                historique.date_fin = timezone.now()
                historique.save()
                
                messages.success(request, f"✅ Rapport '{rapport.titre}' généré avec succès!")
                return redirect('communication:liste_rapports')
                
            except Exception as pdf_error:
                logger.error(f"PDF generation error: {str(pdf_error)}")
                # Update status to error
                rapport.statut = 'erreur'
                rapport.save()
                historique.statut = 'echoue'
                historique.message_erreur = str(pdf_error)
                historique.date_fin = timezone.now()
                historique.save()
                raise pdf_error
                
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            messages.error(request, f"❌ Erreur lors de la génération: {str(e)}")
            return redirect('communication:generer_rapport')    

class TelechargerRapportView(LoginRequiredMixin, View):
    """View to download PDF reports"""
    
    def get(self, request, rapport_id):
        rapport = get_object_or_404(
            RapportPDF, 
            id=rapport_id, 
            utilisateur=request.user
        )
        
        if not rapport.contenu_pdf:
            messages.error(request, "Rapport non disponible")
            return redirect('communication:liste_rapports')
        
        response = HttpResponse(rapport.contenu_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{rapport.generer_nom_fichier()}"'
        return response

class ApercuRapportView(LoginRequiredMixin, View):
    """View to preview PDF reports"""
    
    def get(self, request, rapport_id):
        rapport = get_object_or_404(
            RapportPDF, 
            id=rapport_id, 
            utilisateur=request.user
        )
        
        if not rapport.contenu_pdf:
            return JsonResponse({
                'error': 'Rapport non disponible'
            }, status=404)
        
        response = HttpResponse(rapport.contenu_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{rapport.generer_nom_fichier()}"'
        return response

class DupliquerRapportView(LoginRequiredMixin, View):
    """View to duplicate existing reports"""
    
    def post(self, request, rapport_id):
        original = get_object_or_404(
            RapportPDF, 
            id=rapport_id, 
            utilisateur=request.user
        )
        
        # Create duplicate without PDF file
        duplicate = RapportPDF.objects.create(
            utilisateur=request.user,
            statistique=original.statistique,
            titre=f"Copie de {original.titre}",
            mois=original.mois,
            format_rapport=original.format_rapport,
            template_rapport=original.template_rapport,
            couleur_principale=original.couleur_principale,
            inclure_statistiques=original.inclure_statistiques,
            inclure_graphiques=original.inclure_graphiques,
            inclure_analyse_ia=original.inclure_analyse_ia,
            inclure_journaux=original.inclure_journaux,
            statut='brouillon'
        )
        
        messages.success(request, "Rapport dupliqué avec succès")
        return redirect('communication:liste_rapports')

    
class SupprimerRapportView(LoginRequiredMixin, View):
    """View to delete PDF reports"""
    
    def post(self, request, rapport_id):
        rapport = get_object_or_404(
            RapportPDF, 
            id=rapport_id, 
            utilisateur=request.user
        )
        
        titre_rapport = rapport.titre
        
        try:
            # Delete the report (this will also delete the PDF file due to our model's delete method)
            rapport.delete()
            messages.success(request, f"✅ Rapport '{titre_rapport}' supprimé avec succès")
        except Exception as e:
            logger.error(f"Error deleting report {rapport_id}: {str(e)}")
            messages.error(request, f"❌ Erreur lors de la suppression du rapport: {str(e)}")
        
        return redirect('communication:liste_rapports')


#############################################################################################################################
#############################################################################################################################
# ... Assistant IA Views ...


class AssistantIAView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            journals = Journal.objects.filter(utilisateur=request.user).order_by('-date_creation')[:10]
            conversations_recentes = AssistantIA.objects.filter(
                utilisateur=request.user
            ).select_related('journal').order_by('-date_creation')[:5]
            
            stats = ai_service.get_statistiques_utilisateur(request.user)
            
            context = {
                'journals': journals,
                'conversations_recentes': conversations_recentes,
                'session_id': str(uuid.uuid4()),
                'stats': stats,
                'active_tab': 'assistant_ia',
            }
            return render(request, 'communication/assistant_ia/assistant.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement assistant IA: {str(e)}")
            messages.error(request, "Erreur lors du chargement de l'assistant IA")
            return redirect('users:home')

@method_decorator(ensure_csrf_cookie, name='dispatch')
class EnvoyerMessageView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            journal_id = data.get('journal_id')
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'success': False, 'error': 'Message vide'}, status=400)
            
            if len(message) > 1000:
                return JsonResponse({'success': False, 'error': 'Message trop long (max 1000 caractères)'}, status=400)
            
            if not session_id:
                return JsonResponse({'success': False, 'error': 'Session ID manquant'}, status=400)
            
            journal = None
            if journal_id:
                try:
                    journal_uuid = uuid.UUID(journal_id)
                    journal = Journal.objects.get(id=journal_uuid, utilisateur=request.user)
                except (ValueError, Journal.DoesNotExist):
                    return JsonResponse({'success': False, 'error': 'Journal non trouvé ou non autorisé'}, status=404)
            
            contexte = {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request)
            }
            
            resultat = ai_service.traiter_interaction(
                utilisateur=request.user,
                message=message,
                journal=journal,
                session_id=session_id,
                contexte=contexte
            )
            
            if resultat['success']:
                return JsonResponse({
                    'success': True,
                    'reponse': resultat['reponse'],
                    'date_interaction': resultat['date_interaction'],
                    'type_interaction': resultat['type_interaction'],
                    'statistiques': resultat['statistiques']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': resultat.get('error', 'Erreur lors du traitement du message')
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Données JSON invalides'}, status=400)
        except Exception as e:
            logger.error(f"Erreur envoi message: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Erreur interne du serveur: {str(e)}'}, status=500)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class HistoriqueConversationsView(LoginRequiredMixin, View):
    def get(self, request):
        conversations = AssistantIA.objects.filter(
            utilisateur=request.user
        ).order_by('-date_creation')
        
        sessions = {}
        for conv in conversations:
            if conv.session_id not in sessions:
                sessions[conv.session_id] = []
            sessions[conv.session_id].append(conv)
        
        sessions_json = {}
        for session_id, convs in sessions.items():
            session_key = str(session_id)
            sessions_json[session_key] = [
                {
                    'message_utilisateur': conv.message_utilisateur,
                    'reponse_ia': conv.reponse_ia,
                    'date_creation': conv.date_creation.isoformat(),
                    'type_interaction': conv.type_interaction,
                    'type_interaction_display': conv.get_type_interaction_display(),
                }
                for conv in convs
            ]
        
        context = {
            'sessions': sessions,
            'sessions_json': json.dumps(sessions_json),
            'active_tab': 'assistant_ia',
        }
        return render(request, 'communication/assistant_ia/historique.html', context)

class GetSessionView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        try:
            conversations = AssistantIA.objects.filter(
                utilisateur=request.user,
                session_id=session_id
            ).order_by('date_creation')
            
            data = [{
                'id': str(conv.id),
                'message_utilisateur': conv.message_utilisateur,
                'reponse_ia': conv.reponse_ia,
                'date_interaction': conv.date_creation.strftime('%H:%M'),
                'type_interaction': conv.type_interaction,
                'type_interaction_display': conv.get_type_interaction_display(),
            } for conv in conversations]
            
            return JsonResponse({'conversations': data})
        except Exception as e:
            logger.error(f"Erreur récupération session {session_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Erreur lors de la récupération de la session'}, status=500)

class RefreshJournalsView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            cache_key = f'journals_{request.user.id}'
            journals_data = cache.get(cache_key)
            if not journals_data:
                journals = Journal.objects.filter(utilisateur=request.user).order_by('-date_creation')[:10]
                journals_data = [{
                    'id': str(journal.id),
                    'titre': journal.contenu_texte[:50] + '...' if journal.contenu_texte else f'Journal {journal.date_creation.strftime("%Y-%m-%d")}',
                    'date_creation': journal.date_creation.strftime('%d/%m/%Y'),
                    'contenu': journal.contenu_texte or f'[{journal.type_entree}: {journal.audio.name if journal.audio else journal.image.name if journal.image else "Sans contenu"}]',
                    'type_entree': journal.type_entree,
                    'categorie': journal.categorie or 'Non catégorisé'
                } for journal in journals]
                cache.set(cache_key, journals_data, timeout=300)  # Cache for 5 minutes
            return JsonResponse({'success': True, 'journals': journals_data})
        except Exception as e:
            logger.error(f"Erreur récupération journaux: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Erreur lors de la récupération des journaux'}, status=500)
        

#############################################################################################################################
#############################################################################################################################
# ... SuggestionConnexion Views ...

class SuggestionsConnexionView(LoginRequiredMixin, View):
    """View to display connection suggestions for the user with notification system"""
    
    def get(self, request):
        try:
            filter_type = request.GET.get('filter', 'all')
            selected_user_id = request.GET.get('user_id')
            
            # Get all suggestions involving the user
            all_suggestions = SuggestionConnexion.objects.filter(
                Q(utilisateur_source=request.user) | Q(utilisateur_cible=request.user)
            ).select_related('utilisateur_source', 'utilisateur_cible').order_by('-date_suggestion')
            
            # Filter based on type
            if filter_type == 'received':
                suggestions = all_suggestions.filter(utilisateur_cible=request.user)
            elif filter_type == 'sent':
                suggestions = all_suggestions.filter(utilisateur_source=request.user)
            elif filter_type == 'accepted':
                suggestions = all_suggestions.filter(statut='acceptee')
            elif filter_type == 'ignored':
                suggestions = all_suggestions.filter(statut='ignoree')
            else:
                suggestions = all_suggestions
            
            # Get selected user profile if user_id is provided
            selected_user = None
            if selected_user_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    selected_user = User.objects.get(id=selected_user_id)
                except User.DoesNotExist:
                    pass
            
            context = {
                'suggestions': suggestions,
                'all_suggestions': all_suggestions,
                'filter_type': filter_type,
                'selected_user': selected_user,
                'active_tab': 'suggestions',
                'types_suggestion': SuggestionConnexion.TYPE_SUGGESTION_CHOICES,
            }
            return render(request, 'communication/suggestions/liste_suggestions.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement suggestions: {str(e)}")
            messages.error(request, "Erreur lors du chargement des suggestions")
            return redirect('communication:dashboard')


class AccepterSuggestionView(LoginRequiredMixin, View):
    """View to accept a connection suggestion"""
    
    def post(self, request, suggestion_id):
        try:
            suggestion = get_object_or_404(
                SuggestionConnexion,
                id=suggestion_id,
                utilisateur_cible=request.user,
                statut='proposee'
            )
            
            # Update suggestion status
            suggestion.statut = 'acceptee'
            suggestion.save()
            
            # Create reverse suggestion if it doesn't exist (but keep it as 'proposee')
            reverse_suggestion, created = SuggestionConnexion.objects.get_or_create(
                utilisateur_source=request.user,
                utilisateur_cible=suggestion.utilisateur_source,
                defaults={
                    'score_similarite': suggestion.score_similarite,
                    'type_suggestion': suggestion.type_suggestion,
                    'statut': 'proposee'  # Keep as proposed, not auto-accepted
                }
            )
            
            # Don't auto-accept the reverse suggestion - let the other user decide
            
            messages.success(request, f"✅ Connexion acceptée avec {suggestion.utilisateur_source.username}!")
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur acceptation suggestion {suggestion_id}: {str(e)}")
            messages.error(request, "Erreur lors de l'acceptation de la suggestion")
            return redirect('communication:suggestions')


class IgnorerSuggestionView(LoginRequiredMixin, View):
    """View to ignore a connection suggestion"""
    
    def post(self, request, suggestion_id):
        try:
            suggestion = get_object_or_404(
                SuggestionConnexion,
                id=suggestion_id,
                utilisateur_cible=request.user,
                statut='proposee'
            )
            
            suggestion.statut = 'ignoree'
            suggestion.save()
            
            messages.info(request, f"Suggestion de {suggestion.utilisateur_source.username} ignorée")
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur ignore suggestion {suggestion_id}: {str(e)}")
            messages.error(request, "Erreur lors de l'ignorance de la suggestion")
            return redirect('communication:suggestions')


class GenererSuggestionsView(LoginRequiredMixin, View):
    """View to generate new connection suggestions"""
    
    def post(self, request):
        try:
            # This would typically call a service to generate suggestions
            # For now, we'll create a simple implementation
            
            # Get user's recent journal entries for analysis
            recent_journals = Journal.objects.filter(
                utilisateur=request.user
            ).order_by('-date_creation')[:10]
            
            if not recent_journals.exists():
                messages.warning(request, "Vous devez avoir des entrées de journal pour générer des suggestions")
                return redirect('communication:suggestions')
            
            # Simple suggestion logic (in a real app, this would use AI/ML)
            suggestions_created = self._generer_suggestions_simples(request.user)
            
            if suggestions_created > 0:
                messages.success(request, f"✅ {suggestions_created} nouvelle(s) suggestion(s) générée(s)!")
            else:
                messages.info(request, "Aucune nouvelle suggestion trouvée pour le moment")
            
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur génération suggestions: {str(e)}")
            messages.error(request, "Erreur lors de la génération des suggestions")
            return redirect('communication:suggestions')
    
    def _generer_suggestions_simples(self, user):
        """Simple suggestion generation logic"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get other users who have journals
        other_users = User.objects.exclude(id=user.id).filter(
            journal__isnull=False
        ).distinct()[:5]  # Limit to 5 suggestions
        
        suggestions_created = 0
        
        for other_user in other_users:
            # Check if suggestion already exists
            if SuggestionConnexion.objects.filter(
                utilisateur_source=user,
                utilisateur_cible=other_user
            ).exists():
                continue
            
            # Simple similarity score based on journal count
            user_journal_count = Journal.objects.filter(utilisateur=user).count()
            other_journal_count = Journal.objects.filter(utilisateur=other_user).count()
            
            # Calculate similarity score (simplified)
            similarity_score = min(user_journal_count, other_journal_count) / max(user_journal_count, other_journal_count, 1)
            
            if similarity_score > 0.3:  # Only suggest if similarity > 30%
                SuggestionConnexion.objects.create(
                    utilisateur_source=user,
                    utilisateur_cible=other_user,
                    score_similarite=similarity_score,
                    type_suggestion='objectif_similaire'
                )
                suggestions_created += 1
        
        return suggestions_created


class SupprimerConnexionView(LoginRequiredMixin, View):
    """View to remove an accepted connection"""
    
    def post(self, request, suggestion_id):
        try:
            suggestion = get_object_or_404(
                SuggestionConnexion,
                id=suggestion_id,
                statut='acceptee'
            )
            
            # Check if user is part of this connection
            if suggestion.utilisateur_source != request.user and suggestion.utilisateur_cible != request.user:
                messages.error(request, "Vous n'êtes pas autorisé à supprimer cette connexion")
                return redirect('communication:suggestions')
            
            # Find and update both directions of the connection
            SuggestionConnexion.objects.filter(
                Q(utilisateur_source=suggestion.utilisateur_source, utilisateur_cible=suggestion.utilisateur_cible) |
                Q(utilisateur_source=suggestion.utilisateur_cible, utilisateur_cible=suggestion.utilisateur_source),
                statut='acceptee'
            ).update(statut='ignoree')
            
            other_user = suggestion.utilisateur_cible if suggestion.utilisateur_source == request.user else suggestion.utilisateur_source
            messages.success(request, f"Connexion avec {other_user.username} supprimée")
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur suppression connexion {suggestion_id}: {str(e)}")
            messages.error(request, "Erreur lors de la suppression de la connexion")
            return redirect('communication:suggestions')


class VoirProfilView(LoginRequiredMixin, View):
    """View to display user profile"""
    
    def get(self, request, user_id):
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get the user profile
            profile_user = get_object_or_404(User, id=user_id)
            
            # Check if there's a connection between current user and profile user
            connection_exists = SuggestionConnexion.objects.filter(
                Q(utilisateur_source=request.user, utilisateur_cible=profile_user) |
                Q(utilisateur_source=profile_user, utilisateur_cible=request.user),
                statut='acceptee'
            ).exists()
            
            # Get recent journal entries (if accessible)
            recent_journals = []
            try:
                from journal.models import Journal
                recent_journals = Journal.objects.filter(
                    utilisateur=profile_user
                ).order_by('-date_creation')[:5]
            except ImportError:
                pass
            
            # Get user statistics (if accessible)
            user_stats = None
            try:
                from dashboard.models import Statistique
                user_stats = Statistique.objects.filter(
                    utilisateur=profile_user
                ).order_by('-periode')[:3]
            except ImportError:
                pass
            
            context = {
                'profile_user': profile_user,
                'connection_exists': connection_exists,
                'recent_journals': recent_journals,
                'user_stats': user_stats,
                'active_tab': 'profile',
            }
            return render(request, 'communication/profile/user_profile.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement profil {user_id}: {str(e)}")
            messages.error(request, "Erreur lors du chargement du profil")
            return redirect('communication:suggestions')
        





