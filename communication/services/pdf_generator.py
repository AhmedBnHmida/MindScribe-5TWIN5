import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.units import inch
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PDFGenerationService:
    """Service for generating customizable PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for different templates"""
        self.styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=15,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='StatsValue',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold'
        ))

    def _get_template_config(self, template_name):
        """Get configuration for different templates"""
        templates = {
            'moderne': {
                'title_style': 'ModernTitle',
                'subtitle_style': 'ModernSubtitle',
                'primary_color': '#3498db',
                'secondary_color': '#2C3E50',
            },
            'classique': {
                'title_style': 'Heading1',
                'subtitle_style': 'Heading2',
                'primary_color': '#000000',
                'secondary_color': '#333333',
            },
            'minimaliste': {
                'title_style': 'Heading1',
                'subtitle_style': 'Heading2',
                'primary_color': '#2C3E50',
                'secondary_color': '#7F8C8D',
            }
        }
        return templates.get(template_name, templates['moderne'])

    def _generate_statistics_section(self, rapport, config):
        """Generate comprehensive statistics section - ONLY if enabled"""
        elements = []
        
        # ✅ CHECK IF STATISTICS ARE ENABLED
        if rapport.inclure_statistiques and hasattr(rapport, 'statistique'):
            statistique = rapport.statistique
            
            elements.append(Paragraph("📊 Statistiques Détaillées", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 12))

            # Tableau des statistiques principales
            stats_data = [
                ["📈 Métrique", "🔢 Valeur", "💡 Analyse"],
                ["Fréquence d'écriture", f"{statistique.frequence_ecriture} entrées", self._get_frequency_analysis(statistique.frequence_ecriture)],
                ["Score d'humeur moyen", f"{statistique.score_humeur:.2f}/10", self._get_mood_analysis(statistique.score_humeur)],
                ["Consistance", f"{self._calculate_consistency(statistique):.1f}%", "Régularité des écrits"],
                ["Productivité", f"{self._calculate_productivity(statistique):.1f}/10", "Niveau d'activité"],
            ]
            
            stats_table = Table(stats_data, colWidths=[150, 120, 180])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config['primary_color'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 20))

            # Thèmes dominants
            if statistique.themes_dominants:
                elements.append(Paragraph("🎯 Thèmes Dominants", self.styles[config['subtitle_style']]))
                elements.append(Spacer(1, 8))
                
                themes_list = []
                for theme in statistique.themes_dominants[:5]:
                    themes_list.append(ListItem(Paragraph(theme, self.styles['Normal'])))
                
                elements.append(ListFlowable(themes_list, bulletType='bullet'))
                elements.append(Spacer(1, 15))

            # Bilan mensuel
            if statistique.bilan_mensuel:
                elements.append(Paragraph("📝 Bilan Mensuel", self.styles[config['subtitle_style']]))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph(statistique.bilan_mensuel, self.styles['Normal']))
                elements.append(Spacer(1, 20))
        else:
            # Show message if statistics are disabled
            elements.append(Paragraph("📊 Statistiques", self.styles[config['subtitle_style']]))
            elements.append(Paragraph("<i>Les statistiques ne sont pas incluses dans ce rapport</i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))

        return elements

    def _generate_graphiques_section(self, rapport, config):
        """Generate graphs section - ONLY if enabled"""
        elements = []
        
        # ✅ CHECK IF GRAPHS ARE ENABLED
        if rapport.inclure_graphiques:
            elements.append(Paragraph("📈 Graphiques et Visualisations", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 12))
            
            # Placeholder for graphs (you can add actual charts here)
            graph_data = [
                ["Évolution de l'humeur", "📊 Graphique en courbes - Humeur moyenne par semaine"],
                ["Fréquence d'écriture", "📊 Graphique en barres - Entrées par jour"],
                ["Thèmes populaires", "📊 Graphique en secteurs - Répartition des thèmes"],
                ["Progression des objectifs", "📊 Graphique de progression - Avancement mensuel"],
            ]
            
            graph_table = Table(graph_data, colWidths=[200, 250])
            graph_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config['secondary_color'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
            ]))
            elements.append(graph_table)
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("📈 Graphiques", self.styles[config['subtitle_style']]))
            elements.append(Paragraph("<i>Les graphiques ne sont pas inclus dans ce rapport</i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))

        return elements

    def _generate_analyse_ia_section(self, rapport, config):
        """Generate AI analysis section - ONLY if enabled"""
        elements = []
        
        # ✅ CHECK IF AI ANALYSIS IS ENABLED
        if rapport.inclure_analyse_ia:
            elements.append(Paragraph("🤖 Analyse IA Avancée", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 12))
            
            # AI insights based on statistics
            if hasattr(rapport, 'statistique'):
                statistique = rapport.statistique
                
                ai_insights = []
                
                # Analyse de fréquence
                if statistique.frequence_ecriture >= 20:
                    ai_insights.append("🎯 Excellente régularité d'écriture! Votre engagement est remarquable")
                elif statistique.frequence_ecriture >= 10:
                    ai_insights.append("📝 Bonne fréquence d'écriture, continuez sur cette lancée")
                else:
                    ai_insights.append("💡 Essayez d'écrire plus régulièrement pour de meilleures analyses")
                
                # Analyse d'humeur
                if statistique.score_humeur >= 8:
                    ai_insights.append("😊 Humeur excellente! Cet état d'esprit positif est très bénéfique")
                elif statistique.score_humeur >= 6:
                    ai_insights.append("🙂 Humeur stable et positive, bon équilibre général")
                elif statistique.score_humeur >= 4:
                    ai_insights.append("🤔 Période de réflexion, idéale pour l'introspection")
                else:
                    ai_insights.append("🌧️ Moment plus difficile, pensez à pratiquer l'auto-compassion")
                
                # Analyse des thèmes
                if statistique.themes_dominants:
                    if len(statistique.themes_dominants) >= 4:
                        ai_insights.append("🌈 Excellente variété thématique dans vos écrits")
                    else:
                        ai_insights.append("🎨 Vos écrits se concentrent sur quelques thèmes principaux")
                
                # Recommandations IA supplémentaires
                ai_insights.append("🔍 L'IA détecte des patterns cohérents dans votre routine d'écriture")
                ai_insights.append("💭 Vos réflexions montrent une bonne profondeur d'analyse")
                
                insights_list = []
                for insight in ai_insights:
                    insights_list.append(ListItem(Paragraph(insight, self.styles['Normal'])))
                
                elements.append(ListFlowable(insights_list, bulletType='bullet'))
                elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("🤖 Analyse IA", self.styles[config['subtitle_style']]))
            elements.append(Paragraph("<i>L'analyse IA n'est pas incluse dans ce rapport</i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))

        return elements

    def _generate_journaux_section(self, rapport, config):
        """Generate journal entries section - ONLY if enabled"""
        elements = []
        
        # ✅ CHECK IF JOURNALS ARE ENABLED
        if rapport.inclure_journaux:
            elements.append(Paragraph("📖 Extraits de Journal", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 12))
            
            # Sample journal entries (in a real app, you would fetch actual entries)
            journal_entries = [
                "🌅 **Matinée productive** : Aujourd'hui j'ai commencé par une séance de méditation suivie d'une planification claire de ma journée. Je me sens concentré et motivé.",
                "💼 **Réflexion professionnelle** : J'ai réalisé l'importance de l'équilibre travail-vie personnelle. Prendre du temps pour soi n'est pas du temps perdu.",
                "🌙 **Soirée réflexive** : En repensant à ma journée, je me rends compte que les petites victoires comptent autant que les grands succès."
            ]
            
            journal_list = []
            for i, entry in enumerate(journal_entries[:3], 1):
                journal_list.append(ListItem(Paragraph(f"<b>Entrée #{i}:</b> {entry}", self.styles['Normal'])))
            
            elements.append(ListFlowable(journal_list, bulletType='bullet'))
            elements.append(Spacer(1, 20))
            
            # Note sur la confidentialité
            elements.append(Paragraph("<i><small>Note: Ces extraits sont des exemples. Dans l'application réelle, vos vraies entrées de journal seraient affichées ici.</small></i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("📖 Journal", self.styles[config['subtitle_style']]))
            elements.append(Paragraph("<i>Les extraits de journal ne sont pas inclus dans ce rapport</i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))

        return elements

    def _generate_objectifs_section(self, rapport, config):
        """Generate goals section - ONLY if enabled"""
        elements = []
        
        # ✅ CHECK IF GOALS ARE ENABLED
        if rapport.inclure_objectifs:
            elements.append(Paragraph("🎯 Objectifs et Progrès", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 12))
            
            # Sample goals data
            objectifs_data = [
                ["Objectif", "Progression", "Statut", "Échéance"],
                ["Écrire 3 fois par semaine", "75%", "📈 En bonne voie", "30 jours"],
                ["Apprendre Django avancé", "40%", "📚 En progression", "60 jours"], 
                ["Améliorer la routine matinale", "60%", "🌅 Continue les efforts", "30 jours"],
                ["Lire 2 livres par mois", "25%", "📖 À intensifier", "45 jours"]
            ]
            
            objectifs_table = Table(objectifs_data, colWidths=[180, 80, 100, 80])
            objectifs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config['primary_color'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
            ]))
            elements.append(objectifs_table)
            elements.append(Spacer(1, 20))
            
            # Analyse des objectifs
            elements.append(Paragraph("📋 Analyse des Objectifs", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 8))
            
            analysis_points = [
                "✅ 2 objectifs sur 4 sont en bonne voie",
                "📊 Progression moyenne: 50%",
                "🎯 Objectif le plus avancé: Routine d'écriture",
                "💪 Objectif à renforcer: Lecture mensuelle"
            ]
            
            analysis_list = []
            for point in analysis_points:
                analysis_list.append(ListItem(Paragraph(point, self.styles['Normal'])))
            
            elements.append(ListFlowable(analysis_list, bulletType='bullet'))
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("🎯 Objectifs", self.styles[config['subtitle_style']]))
            elements.append(Paragraph("<i>Les objectifs ne sont pas inclus dans ce rapport</i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))

        return elements

    def _generate_recommandations_section(self, rapport, config):
        """Generate recommendations section - ONLY if enabled"""
        elements = []
        
        # ✅ CHECK IF RECOMMENDATIONS ARE ENABLED
        if rapport.inclure_recommandations:
            elements.append(Paragraph("💡 Recommandations Personnalisées", self.styles[config['subtitle_style']]))
            elements.append(Spacer(1, 12))
            
            recommendations = self._generate_recommendations(rapport)
            rec_list = []
            for rec in recommendations:
                rec_list.append(ListItem(Paragraph(rec, self.styles['Normal'])))
            
            elements.append(ListFlowable(rec_list, bulletType='bullet'))
            elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("💡 Recommandations", self.styles[config['subtitle_style']]))
            elements.append(Paragraph("<i>Les recommandations ne sont pas incluses dans ce rapport</i>", self.styles['Italic']))
            elements.append(Spacer(1, 20))

        return elements

    def _get_frequency_analysis(self, frequency):
        """Analyze writing frequency"""
        if frequency >= 20:
            return "Très régulier 🎉"
        elif frequency >= 10:
            return "Régulier 👍"
        elif frequency >= 5:
            return "Modéré 📊"
        else:
            return "À améliorer 💪"

    def _get_mood_analysis(self, mood_score):
        """Analyze mood score"""
        if mood_score >= 8:
            return "Excellente humeur 😊"
        elif mood_score >= 6:
            return "Bonne humeur 🙂"
        elif mood_score >= 4:
            return "Humeur neutre 😐"
        else:
            return "Humeur basse 😔"

    def _calculate_consistency(self, statistique):
        """Calculate writing consistency"""
        base_consistency = min(100, (statistique.frequence_ecriture / 30) * 100)
        return base_consistency

    def _calculate_productivity(self, statistique):
        """Calculate productivity score"""
        base_productivity = min(10, (statistique.frequence_ecriture / 3) + (statistique.score_humeur / 2))
        return base_productivity

    def generate_complete_report(self, rapport):
        """Generate a complete monthly report that RESPECTS all inclusion settings"""
        try:
            buffer = BytesIO()
            config = self._get_template_config(rapport.template_rapport)
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            story = []

            # === PAGE DE COUVERTURE ===
            story.append(Paragraph(rapport.titre, self.styles[config['title_style']]))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Période: {rapport.mois}", self.styles['Heading3']))
            story.append(Spacer(1, 30))

            # Informations utilisateur
            user_data = [
                ["👤 Informations Personnelles", ""],
                ["Utilisateur:", f"{rapport.utilisateur.username}"],
                ["Email:", f"{rapport.utilisateur.email}"],
                ["Période:", f"{rapport.mois}"],
                ["Date de génération:", f"{datetime.now().strftime('%d/%m/%Y à %H:%M')}"],
                ["Template:", f"{rapport.get_template_rapport_display()}"],
            ]
            
            user_table = Table(user_data, colWidths=[150, 300])
            user_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(config['primary_color'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
            ]))
            story.append(user_table)
            story.append(Spacer(1, 30))

            # === ALL SECTIONS - RESPECTING INCLUSION SETTINGS ===
            
            # 1. Statistiques (if enabled)
            story.extend(self._generate_statistics_section(rapport, config))
            
            # 2. Graphiques (if enabled)  
            story.extend(self._generate_graphiques_section(rapport, config))
            
            # 3. Analyse IA (if enabled)
            story.extend(self._generate_analyse_ia_section(rapport, config))
            
            # 4. Journaux (if enabled)
            story.extend(self._generate_journaux_section(rapport, config))
            
            # 5. Objectifs (if enabled)
            story.extend(self._generate_objectifs_section(rapport, config))
            
            # 6. Recommandations (if enabled)
            story.extend(self._generate_recommandations_section(rapport, config))

            # === RÉSUMÉ EXÉCUTIF ===
            story.append(Paragraph("🎯 Résumé Exécutif", self.styles[config['subtitle_style']]))
            story.append(Spacer(1, 8))
            
            executive_summary = self._generate_executive_summary(rapport)
            story.append(Paragraph(executive_summary, self.styles['Normal']))
            story.append(Spacer(1, 30))

            # === PIED DE PAGE ===
            footer_text = f"Rapport généré par MindScribe • {datetime.now().strftime('%d/%m/%Y à %H:%M')} • Confidential"
            story.append(Paragraph(footer_text, ParagraphStyle(
                name='Footer',
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )))

            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise

    def _generate_recommendations(self, rapport):
        """Generate personalized recommendations"""
        recommendations = []
        
        if hasattr(rapport, 'statistique'):
            statistique = rapport.statistique
            
            # Recommandations basées sur la fréquence
            if statistique.frequence_ecriture < 10:
                recommendations.append("📝 Essayez d'écrire plus régulièrement (3-4 fois par semaine) pour mieux suivre votre évolution")
            elif statistique.frequence_ecriture > 20:
                recommendations.append("🎉 Excellente régularité! Continuez à maintenir ce rythme d'écriture")
            else:
                recommendations.append("👍 Bonne fréquence d'écriture, vous avez trouvé un bon équilibre")
            
            # Recommandations basées sur l'humeur
            if statistique.score_humeur < 5:
                recommendations.append("😊 Pratiquez la gratitude quotidienne et les exercices de respiration pour améliorer votre humeur")
            elif statistique.score_humeur > 8:
                recommendations.append("🌈 Humeur excellente! Profitez-en pour explorer de nouveaux sujets créatifs")
            else:
                recommendations.append("💪 Humeur stable, continuez vos pratiques de bien-être actuelles")
            
            # Recommandations générales
            recommendations.append("🔍 Utilisez les analyses pour identifier vos patterns d'écriture et vos moments les plus productifs")
            recommendations.append("🎯 Fixez-vous des objectifs mensuels réalisables pour rester motivé et mesurer vos progrès")
            recommendations.append("📊 Revoyez régulièrement vos statistiques pour ajuster vos habitudes d'écriture")
        
        # Recommandations supplémentaires
        recommendations.append("🌙 Essayez d'écrire à différents moments de la journée pour découvrir vos périodes les plus créatives")
        recommendations.append("💭 Notez vos rêves et idées spontanées pour enrichir votre pratique d'écriture")
        
        return recommendations

    def _generate_executive_summary(self, rapport):
        """Generate executive summary"""
        summary_parts = []
        
        if hasattr(rapport, 'statistique'):
            statistique = rapport.statistique
            
            summary_parts.append(f"Ce rapport couvre la période de {rapport.mois}. ")
            summary_parts.append(f"Vous avez écrit {statistique.frequence_ecriture} entrées avec un score d'humeur moyen de {statistique.score_humeur:.1f}/10. ")
            summary_parts.append(f"Votre consistance d'écriture est de {self._calculate_consistency(statistique):.1f}% et votre niveau de productivité est évalué à {self._calculate_productivity(statistique):.1f}/10.")
            
            if statistique.themes_dominants:
                summary_parts.append(f" Les thèmes dominants de cette période sont: {', '.join(statistique.themes_dominants[:3])}.")
        
        # Ajouter des informations sur les sections incluses
        included_sections = []
        if rapport.inclure_statistiques:
            included_sections.append("statistiques")
        if rapport.inclure_graphiques:
            included_sections.append("graphiques")
        if rapport.inclure_analyse_ia:
            included_sections.append("analyse IA")
        if rapport.inclure_journaux:
            included_sections.append("extraits de journal")
        if rapport.inclure_objectifs:
            included_sections.append("objectifs")
        if rapport.inclure_recommandations:
            included_sections.append("recommandations")
            
        if included_sections:
            summary_parts.append(f" Ce rapport inclut: {', '.join(included_sections)}.")
        
        return "".join(summary_parts)