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
                messages.warning(request, f"Un rapport existe déjà pour {statistique.periode}. Vous pouvez le supprimer puis le regénérer.")
                return redirect('communication:liste_rapports')
            
            # ✅ FIX: Proper boolean handling for checkboxes
            def get_boolean_value(field_name, default=False):
                value = data.get(field_name)
                # Checkboxes return 'on' when checked, None when unchecked
                return value == 'on' if value is not None else default

            # Sanitize and validate inputs
            titre = (data.get('titre') or 'Rapport Mensuel').strip()
            if len(titre) > 200:
                titre = titre[:200]

            valid_formats = {choice[0] for choice in RapportPDF.FORMAT_RAPPORT_CHOICES}
            valid_templates = {choice[0] for choice in RapportPDF.TEMPLATE_CHOICES}
            format_rapport = data.get('format_rapport') or 'complet'
            template_rapport = data.get('template_rapport') or 'moderne'
            if format_rapport not in valid_formats:
                format_rapport = 'complet'
            if template_rapport not in valid_templates:
                template_rapport = 'moderne'

            couleur_principale = data.get('couleur_principale') or '#3498db'
            if not (isinstance(couleur_principale, str) and len(couleur_principale) == 7 and couleur_principale.startswith('#')):
                couleur_principale = '#3498db'

            # Create rapport record with proper boolean values
            rapport = RapportPDF.objects.create(
                utilisateur=request.user,
                statistique=statistique,
                titre=titre,
                mois=data.get('mois', statistique.periode),
                format_rapport=format_rapport,
                template_rapport=template_rapport,
                couleur_principale=couleur_principale,
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

# Duplicate report feature removed as requested

    
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
            # Get journals with multimodal support info
            journals = Journal.objects.filter(
                utilisateur=request.user
            ).order_by('-date_creation')[:15].select_related('analyse')
            
            # Get recent conversations with journal info
            conversations_recentes = AssistantIA.objects.filter(
                utilisateur=request.user
            ).select_related('journal').order_by('-date_creation')[:5]
            
            # Get statistics
            stats = ai_service.get_statistiques_utilisateur(request.user)
            
            # Prepare journal data with multimodal indicators
            journals_with_info = []
            for journal in journals:
                journal_info = {
                    'journal': journal,
                    'has_audio': bool(journal.audio),
                    'has_image': bool(journal.image),
                    'has_text': bool(journal.contenu_texte and journal.contenu_texte.strip()),
                    'is_multimodal': (bool(journal.audio) or bool(journal.image)) and bool(journal.contenu_texte and journal.contenu_texte.strip()),
                    'has_analysis': hasattr(journal, 'analyse') and journal.analyse is not None,
                }
                journals_with_info.append(journal_info)
            
            context = {
                'journals': [j['journal'] for j in journals_with_info],
                'journals_with_info': journals_with_info,
                'conversations_recentes': conversations_recentes,
                'session_id': str(uuid.uuid4()),
                'stats': stats,
                'active_tab': 'assistant_ia',
                'total_journals': Journal.objects.filter(utilisateur=request.user).count(),
            }
            return render(request, 'communication/assistant_ia/assistant.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement assistant IA: {str(e)}", exc_info=True)
            messages.error(request, f"Erreur lors du chargement de l'assistant IA: {str(e)}")
            return redirect('communication:dashboard')

@method_decorator(ensure_csrf_cookie, name='dispatch')
class EnvoyerMessageView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            journal_id = data.get('journal_id')
            session_id = data.get('session_id')
            
            # Validation
            if not message:
                return JsonResponse({'success': False, 'error': 'Message vide'}, status=400)
            
            if len(message) > 2000:
                return JsonResponse({'success': False, 'error': 'Message trop long (max 2000 caractères)'}, status=400)
            
            if not session_id:
                return JsonResponse({'success': False, 'error': 'Session ID manquant'}, status=400)
            
            # Get journal with multimodal info
            journal = None
            journal_info = {}
            if journal_id:
                try:
                    journal_uuid = uuid.UUID(journal_id)
                    journal = Journal.objects.select_related('analyse').get(
                        id=journal_uuid, 
                        utilisateur=request.user
                    )
                    
                    # Prepare multimodal info
                    journal_info = {
                        'has_audio': bool(journal.audio),
                        'has_image': bool(journal.image),
                        'has_text': bool(journal.contenu_texte and journal.contenu_texte.strip()),
                        'type_entree': journal.type_entree,
                        'has_analysis': hasattr(journal, 'analyse') and journal.analyse is not None,
                    }
                    
                    logger.info(f"Journal sélectionné: {journal.id}, Type: {journal.type_entree}, Multimodal: {journal_info['has_audio'] or journal_info['has_image']}")
                    
                except (ValueError, Journal.DoesNotExist) as e:
                    logger.warning(f"Journal non trouvé: {journal_id}, Error: {e}")
                    return JsonResponse({'success': False, 'error': 'Journal non trouvé ou non autorisé'}, status=404)
            
            # Context for AI service
            contexte = {
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
                'journal_info': journal_info,
            }
            
            # Process interaction
            resultat = ai_service.traiter_interaction(
                utilisateur=request.user,
                message=message,
                journal=journal,
                session_id=session_id,
                contexte=contexte
            )
            
            if resultat.get('success'):
                response_data = {
                    'success': True,
                    'reponse': resultat.get('reponse', ''),
                    'date_interaction': resultat.get('date_interaction', ''),
                    'type_interaction': resultat.get('type_interaction', 'question'),
                    'type_interaction_display': resultat.get('type_interaction_display', 'Question'),
                    'statistiques': resultat.get('statistiques', {}),
                }
                
                # Add conversation ID if available
                if 'conversation_id' in resultat:
                    response_data['conversation_id'] = resultat['conversation_id']
                
                return JsonResponse(response_data)
            else:
                error_msg = resultat.get('error', 'Erreur lors du traitement du message')
                logger.error(f"Erreur traitement interaction: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
                
        except json.JSONDecodeError as e:
            logger.error(f"Erreur décodage JSON: {e}")
            return JsonResponse({'success': False, 'error': 'Données JSON invalides'}, status=400)
        except Exception as e:
            logger.error(f"Erreur envoi message: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Erreur interne du serveur. Veuillez réessayer.'
            }, status=500)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class HistoriqueConversationsView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # Get all conversations with journal info
            conversations = AssistantIA.objects.filter(
                utilisateur=request.user
            ).select_related('journal').order_by('-date_creation')
            
            # Group by session
            sessions = {}
            for conv in conversations:
                session_key = str(conv.session_id)
                if session_key not in sessions:
                    sessions[session_key] = []
                sessions[session_key].append(conv)
            
            # Sort sessions by most recent (safely handle empty lists)
            def get_first_date(session_pair):
                convs = session_pair[1]
                if convs and len(convs) > 0:
                    return convs[0].date_creation
                return timezone.now()
            
            sessions = dict(sorted(sessions.items(), 
                key=get_first_date,
                reverse=True
            ))
            
            # Sort conversations within each session by date (oldest first for display)
            for session_key in sessions:
                sessions[session_key] = sorted(sessions[session_key], key=lambda x: x.date_creation)
            
            # Prepare JSON data with multimodal info
            sessions_json = {}
            for session_id, convs in sessions.items():
                if not convs:
                    continue
                sessions_json[session_id] = [
                    {
                        'id': str(conv.id),
                        'message_utilisateur': conv.message_utilisateur or '',
                        'reponse_ia': conv.reponse_ia or '',
                        'date_creation': conv.date_creation.isoformat(),
                        'type_interaction': conv.type_interaction or 'question',
                        'type_interaction_display': conv.get_type_interaction_display() or 'Question',
                        'journal_id': str(conv.journal.id) if conv.journal else None,
                        'journal_type': getattr(conv.journal, 'type_entree', None) if conv.journal else None,
                        'multimodal': getattr(conv, 'type_contenu_journal', None) in ['audio', 'image', 'multimodal'] if conv.journal else False,
                        'tokens_utilises': conv.tokens_utilises or 0,
                        'score_confiance': float(conv.score_confiance) if conv.score_confiance else 0.0,
                    }
                    for conv in convs
                ]
            
            # Get stats
            total_sessions = len(sessions)
            total_conversations = conversations.count()
            
            # Ensure sessions_json is properly formatted JSON string
            try:
                sessions_json_str = json.dumps(sessions_json, default=str, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error serializing sessions_json: {str(e)}")
                sessions_json_str = "{}"
            
            context = {
                'sessions': sessions,
                'sessions_json': sessions_json_str,
                'active_tab': 'assistant_ia',
                'total_sessions': total_sessions,
                'total_conversations': total_conversations,
            }
            return render(request, 'communication/assistant_ia/historique.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement historique: {str(e)}", exc_info=True)
            messages.error(request, f"Erreur lors du chargement de l'historique: {str(e)}")
            return redirect('communication:assistant_ia')

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
                journals = Journal.objects.filter(utilisateur=request.user).select_related('analyse').order_by('-date_creation')[:15]
                journals_data = []
                for journal in journals:
                    has_audio = bool(journal.audio)
                    has_image = bool(journal.image)
                    has_text = bool(journal.contenu_texte and journal.contenu_texte.strip())
                    is_multimodal = (has_audio or has_image) and has_text
                    
                    journal_data = {
                        'id': str(journal.id),
                        'titre': journal.contenu_texte[:50] + '...' if journal.contenu_texte else f'Journal {journal.date_creation.strftime("%Y-%m-%d")}',
                        'date_creation': journal.date_creation.strftime('%d/%m/%Y'),
                        'contenu': journal.contenu_texte or f'[{journal.type_entree}: {journal.audio.name if journal.audio else journal.image.name if journal.image else "Sans contenu"}]',
                        'type_entree': journal.type_entree,
                        'categorie': journal.categorie or 'Non catégorisé',
                        'has_audio': has_audio,
                        'has_image': has_image,
                        'has_text': has_text,
                        'multimodal': is_multimodal,
                        'has_analysis': hasattr(journal, 'analyse') and journal.analyse is not None,
                    }
                    journals_data.append(journal_data)
                cache.set(cache_key, journals_data, timeout=300)  # Cache for 5 minutes
            return JsonResponse({'success': True, 'journals': journals_data})
        except Exception as e:
            logger.error(f"Erreur récupération journaux: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': 'Erreur lors de la récupération des journaux'}, status=500)
        

#############################################################################################################################
#############################################################################################################################
# ... SuggestionConnexion Views ...

class SuggestionsConnexionView(LoginRequiredMixin, View):
    """
    View to display connection suggestions FOR the user.
    Shows suggestions where utilisateur_source = current user.
    When user accepts, it sends a connection request to utilisateur_cible.
    """
    
    def get(self, request):
        try:
            from .services.suggestion_service import SuggestionConnexionService
            
            filter_type = request.GET.get('filter', 'all')
            selected_user_id = request.GET.get('user_id')
            
            # Show suggestions where the current user is the SOURCE (utilisateur_source)
            # This means: suggestions shown TO the current user about other users
            all_suggestions = SuggestionConnexion.objects.filter(
                utilisateur_source=request.user
            ).select_related('utilisateur_source', 'utilisateur_cible').order_by('-date_suggestion')
            
            # Filter based on status (all are received by default since we filter above)
            if filter_type == 'proposed' or filter_type == 'received':
                suggestions = all_suggestions.filter(statut='proposee')
            elif filter_type == 'accepted':
                suggestions = all_suggestions.filter(statut='acceptee')
            elif filter_type == 'ignored':
                suggestions = all_suggestions.filter(statut='ignoree')
            else:
                # 'all' - show all statuses
                suggestions = all_suggestions
            
            # Get selected user profile if user_id is provided
            selected_user = None
            connection_exists = False
            recent_journals = []
            similarity_data = None
            
            if selected_user_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    selected_user = User.objects.get(id=selected_user_id)
                    
                    # Check if connection exists (both directions accepted)
                    connection_exists = False
                    if selected_user != request.user:
                        # Check if both directions are accepted
                        suggestion1 = SuggestionConnexion.objects.filter(
                            utilisateur_source=request.user,
                            utilisateur_cible=selected_user,
                            statut='acceptee'
                        ).first()
                        suggestion2 = SuggestionConnexion.objects.filter(
                            utilisateur_source=selected_user,
                            utilisateur_cible=request.user,
                            statut='acceptee'
                        ).first()
                        connection_exists = suggestion1 and suggestion2
                    
                    # Get recent journals for selected user
                    recent_journals = Journal.objects.filter(
                        utilisateur=selected_user
                    ).order_by('-date_creation')[:5]
                    
                    # Calculate current similarity if we want to show it
                    if selected_user != request.user:
                        similarity_data = SuggestionConnexionService.calculate_similarity(
                            request.user,
                            selected_user
                        )
                    
                except User.DoesNotExist:
                    pass
            
            # Count suggestions by status
            suggestions_proposed = all_suggestions.filter(statut='proposee').count()
            suggestions_accepted = all_suggestions.filter(statut='acceptee').count()
            suggestions_ignored = all_suggestions.filter(statut='ignoree').count()
            
            context = {
                'suggestions': suggestions,
                'all_suggestions': all_suggestions,
                'filter_type': filter_type,
                'selected_user': selected_user,
                'connection_exists': connection_exists,
                'recent_journals': recent_journals,
                'similarity_data': similarity_data,
                'active_tab': 'suggestions',
                'types_suggestion': SuggestionConnexion.TYPE_SUGGESTION_CHOICES,
                'counts': {
                    'total': all_suggestions.count(),
                    'proposed': suggestions_proposed,
                    'accepted': suggestions_accepted,
                    'ignored': suggestions_ignored,
                }
            }
            return render(request, 'communication/suggestions/liste_suggestions.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement suggestions: {str(e)}", exc_info=True)
            messages.error(request, "Erreur lors du chargement des suggestions")
            return redirect('communication:dashboard')


class AccepterSuggestionView(LoginRequiredMixin, View):
    """
    View to accept a connection suggestion.
    When accepting a suggestion, it sends a connection request to the other user.
    """
    
    def post(self, request, suggestion_id):
        try:
            suggestion = get_object_or_404(
                SuggestionConnexion,
                id=suggestion_id,
                utilisateur_source=request.user,  # User accepts their own suggestion
                statut='proposee'
            )
            
            # Mark suggestion as accepted
            suggestion.statut = 'acceptee'
            suggestion.save()
            
            # Send connection request to utilisateur_cible (the person we want to connect with)
            demande_connexion = suggestion.envoyer_demande_connexion()
            
            messages.success(
                request,
                f"✅ Suggestion acceptée ! Une demande de connexion a été envoyée à "
                f"{suggestion.utilisateur_cible.username}. "
                f"Il/Elle doit l'accepter pour établir la connexion."
            )
            return redirect('communication:suggestions')
            
        except ValueError as e:
            logger.error(f"Erreur validation: {str(e)}")
            messages.error(request, str(e))
            return redirect('communication:suggestions')
        except Exception as e:
            logger.error(f"Erreur acceptation suggestion {suggestion_id}: {str(e)}", exc_info=True)
            messages.error(request, "Erreur lors de l'acceptation de la suggestion")
            return redirect('communication:suggestions')


class AccepterDemandeConnexionView(LoginRequiredMixin, View):
    """
    View to accept a connection request (when someone accepted your suggestion).
    When both users accept, the connection is established.
    """
    
    def post(self, request, suggestion_id):
        try:
            # Get the connection request (someone accepted our suggestion and sent us a request)
            suggestion = get_object_or_404(
                SuggestionConnexion,
                id=suggestion_id,
                utilisateur_cible=request.user,
                statut='proposee'
            )
            
            # Accept the connection request
            connexion_etablie = suggestion.accepter_demande_connexion()
            
            if connexion_etablie:
                messages.success(
                    request,
                    f"🎉 Connexion établie avec {suggestion.utilisateur_source.username} ! "
                    f"Vous êtes maintenant connectés."
                )
            else:
                messages.success(
                    request,
                    f"✅ Demande de connexion acceptée. "
                    f"En attente que {suggestion.utilisateur_source.username} accepte également."
                )
            
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur acceptation demande {suggestion_id}: {str(e)}", exc_info=True)
            messages.error(request, "Erreur lors de l'acceptation de la demande")
            return redirect('communication:suggestions')


class IgnorerSuggestionView(LoginRequiredMixin, View):
    """View to ignore a connection suggestion"""
    
    def post(self, request, suggestion_id):
        try:
            suggestion = get_object_or_404(
                SuggestionConnexion,
                id=suggestion_id,
                utilisateur_source=request.user,  # User ignores their own suggestion
                statut='proposee'
            )
            
            suggestion.statut = 'ignoree'
            suggestion.save()
            
            messages.info(request, f"Suggestion de connexion avec {suggestion.utilisateur_cible.username} ignorée")
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur ignore suggestion {suggestion_id}: {str(e)}")
            messages.error(request, "Erreur lors de l'ignorance de la suggestion")
            return redirect('communication:suggestions')


class GenererSuggestionsView(LoginRequiredMixin, View):
    """View to generate new connection suggestions using enhanced similarity matching"""
    
    def post(self, request):
        try:
            from .services.suggestion_service import SuggestionConnexionService
            
            # Check if user has profile data filled (for better matching)
            user = request.user
            has_profile_data = (
                (user.objectifs_personnels and len(user.objectifs_personnels) > 0) or
                (user.centres_interet and len(user.centres_interet) > 0) or
                user.humeur_generale
            )
            
            if not has_profile_data:
                messages.warning(
                    request,
                    "💡 Astuce: Remplissez votre profil (objectifs, centres d'intérêt, humeur) "
                    "pour obtenir de meilleures suggestions de connexion !"
                )
            
            # Generate suggestions using enhanced service
            suggestions_created = SuggestionConnexionService.generate_suggestions_for_user(user)
            
            if suggestions_created > 0:
                messages.success(
                    request, 
                    f"✅ {suggestions_created} nouvelle(s) suggestion(s) générée(s) basée(s) sur votre profil !"
                )
            else:
                messages.info(
                    request, 
                    "Aucune nouvelle suggestion trouvée pour le moment. "
                    "Assurez-vous d'avoir rempli votre profil pour de meilleurs résultats."
                )
            
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur génération suggestions: {str(e)}", exc_info=True)
            messages.error(request, "Erreur lors de la génération des suggestions")
            return redirect('communication:suggestions')


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
            # Redirect to connections page if it was an established connection, otherwise suggestions
            if suggestion.est_connexion_etablie:
                return redirect('communication:connexions')
            return redirect('communication:suggestions')
            
        except Exception as e:
            logger.error(f"Erreur suppression connexion {suggestion_id}: {str(e)}")
            messages.error(request, "Erreur lors de la suppression de la connexion")
            return redirect('communication:suggestions')


class ListeConnexionsView(LoginRequiredMixin, View):
    """
    View to display established connections for the user.
    Shows all users the current user is connected to (both suggestions are 'acceptee').
    """
    
    def get(self, request):
        try:
            from .services.suggestion_service import SuggestionConnexionService
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            selected_user_id = request.GET.get('user_id')
            
            # Get all established connections (where both directions are accepted)
            # We need to find suggestions where:
            # 1. The user is either source or target
            # 2. Both directions have statut='acceptee'
            connections = []
            connection_ids = set()
            
            # Get all accepted suggestions involving the user
            accepted_suggestions = SuggestionConnexion.objects.filter(
                Q(utilisateur_source=request.user) | Q(utilisateur_cible=request.user),
                statut='acceptee'
            ).select_related('utilisateur_source', 'utilisateur_cible')
            
            for suggestion in accepted_suggestions:
                # Get the other user
                other_user = suggestion.utilisateur_cible if suggestion.utilisateur_source == request.user else suggestion.utilisateur_source
                
                # Check if reverse suggestion also exists and is accepted
                reverse_exists = SuggestionConnexion.objects.filter(
                    utilisateur_source=other_user,
                    utilisateur_cible=request.user,
                    statut='acceptee'
                ).exists()
                
                if reverse_exists and other_user.id not in connection_ids:
                    connection_ids.add(other_user.id)
                    
                    # Get similarity data - always calculate fresh for accurate scores
                    similarity_data = None
                    try:
                        similarity_data = SuggestionConnexionService.calculate_similarity(
                            request.user,
                            other_user
                        )
                    except Exception as e:
                        logger.warning(f"Error calculating similarity for {other_user.username}: {e}")
                        similarity_data = None
                    
                    # Get recent journals
                    recent_journals = Journal.objects.filter(
                        utilisateur=other_user
                    ).order_by('-date_creation')[:3]
                    
                    connections.append({
                        'user': other_user,
                        'suggestion': suggestion,
                        'similarity_data': similarity_data,
                        'recent_journals': recent_journals,
                        'connection_date': suggestion.date_suggestion,
                    })
            
            # Sort by connection date (most recent first)
            connections.sort(key=lambda x: x['connection_date'], reverse=True)
            
            # Get selected user profile if user_id is provided
            selected_user = None
            selected_connection = None
            recent_journals = []
            similarity_data = None
            
            if selected_user_id:
                try:
                    selected_user = User.objects.get(id=selected_user_id)
                    
                    # Find the connection data for this user
                    for conn in connections:
                        if conn['user'].id == selected_user.id:
                            selected_connection = conn
                            recent_journals = conn['recent_journals']
                            similarity_data = conn['similarity_data']
                            break
                    
                    # Always recalculate similarity for fresh/accurate data
                    if selected_user and selected_user != request.user:
                        try:
                            similarity_data = SuggestionConnexionService.calculate_similarity(
                                request.user,
                                selected_user
                            )
                            # Update the selected_connection dict with fresh data
                            if selected_connection:
                                selected_connection['similarity_data'] = similarity_data
                        except Exception as e:
                            logger.error(f"Error recalculating similarity: {e}", exc_info=True)
                            similarity_data = None
                    
                except User.DoesNotExist:
                    pass
            
            context = {
                'connections': connections,
                'selected_user': selected_user,
                'selected_connection': selected_connection,
                'recent_journals': recent_journals,
                'similarity_data': similarity_data,
                'active_tab': 'connections',
                'connection_count': len(connections),
            }
            return render(request, 'communication/suggestions/liste_connexions.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement connexions: {str(e)}", exc_info=True)
            messages.error(request, "Erreur lors du chargement des connexions")
            return redirect('communication:dashboard')


class VoirProfilView(LoginRequiredMixin, View):
    """View to display user profile with enhanced similarity information"""
    
    def get(self, request, user_id):
        try:
            from django.contrib.auth import get_user_model
            from .services.suggestion_service import SuggestionConnexionService
            User = get_user_model()
            
            # Get the user profile
            profile_user = get_object_or_404(User, id=user_id)
            
            # Check if there's a connection between current user and profile user
            connection_exists = SuggestionConnexion.objects.filter(
                Q(utilisateur_source=request.user, utilisateur_cible=profile_user) |
                Q(utilisateur_source=profile_user, utilisateur_cible=request.user),
                statut='acceptee'
            ).exists()
            
            # Get existing suggestion if any
            existing_suggestion = None
            if profile_user != request.user:
                existing_suggestion = SuggestionConnexion.objects.filter(
                    Q(utilisateur_source=request.user, utilisateur_cible=profile_user) |
                    Q(utilisateur_source=profile_user, utilisateur_cible=request.user)
                ).first()
                
                # Calculate current similarity if no existing suggestion or to show updated score
                similarity_data = SuggestionConnexionService.calculate_similarity(
                    request.user,
                    profile_user
                )
            else:
                similarity_data = None
            
            # Get recent journal entries (if accessible)
            recent_journals = []
            try:
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
                'similarity_data': similarity_data,
                'existing_suggestion': existing_suggestion,
                'active_tab': 'profile',
            }
            return render(request, 'communication/profile/user_profile.html', context)
            
        except Exception as e:
            logger.error(f"Erreur chargement profil {user_id}: {str(e)}", exc_info=True)
            messages.error(request, "Erreur lors du chargement du profil")
            return redirect('communication:suggestions')
        





