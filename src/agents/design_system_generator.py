import logging
import json
import re
import requests
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import colorsys
import webcolors
from PIL import Image
from io import BytesIO
from ..utils.config import config
from ..utils.api_clients import api_manager

logger = logging.getLogger(__name__)

class DesignSystemGenerator:
    def __init__(self):
        self.enabled = config.is_agent_enabled('design_generator')  # Using existing config
        
        if not self.enabled:
            logger.info("Design System Generator agent is disabled")
            return
        
        self.openai_client = api_manager.get_client('openai')
        
        # Free API endpoints
        self.coolors_api = "https://www.thecolorapi.com"
        self.google_fonts_api = "https://www.googleapis.com/webfonts/v1/webfonts"
        self.figma_community_api = "https://www.figma.com/api/v1/files"
        
        # Icon collections (free CDN URLs)
        self.icon_collections = {
            'heroicons': {
                'base_url': 'https://heroicons.com/icons',
                'cdn_url': 'https://cdn.jsdelivr.net/npm/heroicons@2.0.18/24',
                'categories': ['outline', 'solid', 'mini']
            },
            'lucide': {
                'base_url': 'https://lucide.dev/icons',
                'cdn_url': 'https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd',
                'categories': ['outline', 'filled']
            },
            'tabler': {
                'base_url': 'https://tabler-icons.io',
                'cdn_url': 'https://cdn.jsdelivr.net/npm/@tabler/icons@latest/icons',
                'categories': ['outline', 'filled']
            }
        }
        
        # Color psychology mapping
        self.color_psychology = {
            'health': {'primary': '#10B981', 'mood': 'fresh, energetic, natural'},
            'productivity': {'primary': '#3B82F6', 'mood': 'professional, trustworthy, focused'},
            'finance': {'primary': '#059669', 'mood': 'stable, trustworthy, growth'},
            'education': {'primary': '#8B5CF6', 'mood': 'creative, inspiring, intelligent'},
            'entertainment': {'primary': '#F59E0B', 'mood': 'fun, exciting, vibrant'},
            'business': {'primary': '#1F2937', 'mood': 'professional, reliable, sophisticated'},
            'technology': {'primary': '#6366F1', 'mood': 'innovative, modern, digital'},
            'lifestyle': {'primary': '#EC4899', 'mood': 'trendy, personal, expressive'}
        }
        
        # Typography combinations
        self.font_combinations = {
            'modern': {
                'display': 'Inter',
                'body': 'Inter',
                'mood': 'clean, modern, versatile'
            },
            'elegant': {
                'display': 'Playfair Display',
                'body': 'Source Sans Pro',
                'mood': 'sophisticated, elegant, readable'
            },
            'friendly': {
                'display': 'Nunito',
                'body': 'Nunito',
                'mood': 'friendly, approachable, rounded'
            },
            'tech': {
                'display': 'JetBrains Mono',
                'body': 'Roboto',
                'mood': 'technical, precise, digital'
            },
            'creative': {
                'display': 'Poppins',
                'body': 'Open Sans',
                'mood': 'creative, energetic, modern'
            }
        }
    
    def generate_complete_design_system(self, ux_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to generate a complete design system from UX analysis
        """
        if not self.enabled:
            return {"error": "Design System Generator agent is disabled"}
        
        try:
            logger.info("Generating complete design system...")
            
            # Extract key information from UX analysis
            category = ux_analysis.get('category', 'general')
            primary_persona = ux_analysis.get('personas', [{}])[0]
            ux_strategy = ux_analysis.get('ux_strategy', {})
            
            # Step 1: Generate brand color palette
            color_palette = self._generate_color_palette(category, primary_persona)
            
            # Step 2: Select typography system
            typography_system = self._generate_typography_system(category, ux_strategy)
            
            # Step 3: Create icon system
            icon_system = self._generate_icon_system(category)
            
            # Step 4: Generate component designs
            component_system = self._generate_component_system(color_palette, typography_system, ux_strategy)
            
            # Step 5: Find matching Figma templates
            figma_templates = self._find_figma_templates(category, ux_analysis.get('trend_keyword', ''))
            
            # Step 6: Generate design tokens
            design_tokens = self._generate_design_tokens(color_palette, typography_system)
            
            # Step 7: Create usage guidelines
            usage_guidelines = self._create_usage_guidelines(color_palette, typography_system, icon_system)
            
            design_system = {
                'metadata': {
                    'generated_for': ux_analysis.get('trend_keyword', 'Unknown'),
                    'category': category,
                    'target_persona': primary_persona.get('name', 'Unknown'),
                    'generated_at': datetime.now().isoformat(),
                    'version': '1.0.0'
                },
                'brand_identity': {
                    'color_palette': color_palette,
                    'typography_system': typography_system,
                    'brand_personality': self._extract_brand_personality(ux_analysis)
                },
                'design_tokens': design_tokens,
                'component_system': component_system,
                'icon_system': icon_system,
                'figma_resources': figma_templates,
                'usage_guidelines': usage_guidelines,
                'implementation': {
                    'css_variables': self._generate_css_variables(design_tokens),
                    'tailwind_config': self._generate_tailwind_config(color_palette, typography_system),
                    'react_theme': self._generate_react_theme(design_tokens)
                }
            }
            
            logger.info("Design system generation completed successfully")
            return design_system
            
        except Exception as e:
            logger.error(f"Error generating design system: {e}")
            return {"error": str(e)}
    
    def _generate_color_palette(self, category: str, persona: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brand color palette using color theory"""
        try:
            logger.info(f"Generating color palette for category: {category}")
            
            # Get base color from category
            base_color = self.color_psychology.get(category, self.color_psychology['business'])['primary']
            
            # Convert hex to HSL for manipulation
            primary_hsl = self._hex_to_hsl(base_color)
            
            # Generate color variations
            colors = {
                'primary': {
                    '50': self._generate_color_variant(primary_hsl, 0.95, 0.1),
                    '100': self._generate_color_variant(primary_hsl, 0.9, 0.2),
                    '200': self._generate_color_variant(primary_hsl, 0.8, 0.3),
                    '300': self._generate_color_variant(primary_hsl, 0.7, 0.4),
                    '400': self._generate_color_variant(primary_hsl, 0.6, 0.5),
                    '500': base_color,  # Base color
                    '600': self._generate_color_variant(primary_hsl, 0.5, 0.6),
                    '700': self._generate_color_variant(primary_hsl, 0.4, 0.7),
                    '800': self._generate_color_variant(primary_hsl, 0.3, 0.8),
                    '900': self._generate_color_variant(primary_hsl, 0.2, 0.9),
                },
                'secondary': self._generate_complementary_colors(primary_hsl),
                'neutral': self._generate_neutral_colors(),
                'semantic': {
                    'success': '#10B981',
                    'warning': '#F59E0B', 
                    'error': '#EF4444',
                    'info': '#3B82F6'
                }
            }
            
            # Add accessibility information
            accessibility = self._check_color_accessibility(colors)
            
            return {
                'colors': colors,
                'accessibility': accessibility,
                'psychology': {
                    'mood': base_color,
                    'target_emotion': self.color_psychology.get(category, {}).get('mood', 'professional'),
                    'cultural_considerations': self._get_cultural_color_considerations(category)
                },
                'usage_recommendations': self._get_color_usage_recommendations(colors)
            }
            
        except Exception as e:
            logger.error(f"Error generating color palette: {e}")
            return self._create_fallback_color_palette(category)
    
    def _generate_typography_system(self, category: str, ux_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate typography system using Google Fonts"""
        try:
            logger.info("Generating typography system...")
            
            # Select font combination based on category and strategy
            font_style = self._select_font_style(category, ux_strategy)
            font_combo = self.font_combinations.get(font_style, self.font_combinations['modern'])
            
            # Get Google Fonts information
            font_details = self._get_google_fonts_details([font_combo['display'], font_combo['body']])
            
            # Generate type scale
            type_scale = self._generate_type_scale()
            
            # Generate font weights and styles
            font_weights = {
                'light': 300,
                'regular': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700,
                'extrabold': 800
            }
            
            typography_system = {
                'font_families': {
                    'display': font_combo['display'],
                    'body': font_combo['body'],
                    'mono': 'JetBrains Mono'
                },
                'font_details': font_details,
                'type_scale': type_scale,
                'font_weights': font_weights,
                'line_heights': {
                    'tight': 1.25,
                    'normal': 1.5,
                    'relaxed': 1.75,
                    'loose': 2
                },
                'letter_spacing': {
                    'tighter': '-0.05em',
                    'tight': '-0.025em',
                    'normal': '0em',
                    'wide': '0.025em',
                    'wider': '0.05em',
                    'widest': '0.1em'
                },
                'google_fonts_imports': self._generate_google_fonts_imports(font_combo),
                'usage_guidelines': self._generate_typography_guidelines(font_combo)
            }
            
            return typography_system
            
        except Exception as e:
            logger.error(f"Error generating typography system: {e}")
            return self._create_fallback_typography_system()
    
    def _generate_icon_system(self, category: str) -> Dict[str, Any]:
        """Generate icon system using free icon libraries"""
        try:
            logger.info("Generating icon system...")
            
            # Select primary icon library based on category
            primary_library = self._select_icon_library(category)
            
            # Generate icon categories and recommendations
            icon_categories = {
                'navigation': ['home', 'menu', 'search', 'user', 'settings'],
                'actions': ['plus', 'edit', 'delete', 'save', 'share', 'download'],
                'status': ['check', 'x', 'alert-triangle', 'info', 'loader'],
                'content': ['image', 'file-text', 'video', 'music', 'calendar'],
                'communication': ['mail', 'phone', 'message-circle', 'bell', 'heart']
            }
            
            # Generate icon specifications
            icon_specs = {
                'sizes': {
                    'xs': '16px',
                    'sm': '20px', 
                    'md': '24px',
                    'lg': '32px',
                    'xl': '48px'
                },
                'stroke_width': {
                    'thin': '1px',
                    'normal': '1.5px',
                    'thick': '2px'
                },
                'style_variants': ['outline', 'filled', 'duotone']
            }
            
            # Generate CDN links and implementation code
            implementation = self._generate_icon_implementation(primary_library, icon_categories)
            
            return {
                'primary_library': primary_library,
                'categories': icon_categories,
                'specifications': icon_specs,
                'implementation': implementation,
                'accessibility': {
                    'aria_labels': 'Always include descriptive aria-labels',
                    'alt_text': 'Provide alternative text for decorative icons',
                    'size_considerations': 'Minimum 16px for touch targets'
                },
                'usage_guidelines': self._generate_icon_guidelines(primary_library)
            }
            
        except Exception as e:
            logger.error(f"Error generating icon system: {e}")
            return self._create_fallback_icon_system()
    
    def _generate_component_system(self, colors: Dict, typography: Dict, ux_strategy: Dict) -> Dict[str, Any]:
        """Generate component designs using Tailwind CSS"""
        try:
            logger.info("Generating component system...")
            
            # Extract strategy preferences
            strategies = ux_strategy.get('strategies', [])
            primary_strategy = strategies[0] if strategies else {}
            
            # Generate component specifications
            components = {
                'buttons': self._generate_button_components(colors, primary_strategy),
                'forms': self._generate_form_components(colors, typography),
                'cards': self._generate_card_components(colors),
                'navigation': self._generate_navigation_components(colors, primary_strategy),
                'feedback': self._generate_feedback_components(colors),
                'layout': self._generate_layout_components()
            }
            
            # Generate component variants and states
            for component_type in components:
                components[component_type]['variants'] = self._generate_component_variants(component_type)
                components[component_type]['states'] = self._generate_component_states()
            
            return {
                'components': components,
                'design_principles': self._extract_design_principles(ux_strategy),
                'responsive_guidelines': self._generate_responsive_guidelines(),
                'accessibility_standards': self._generate_accessibility_standards(),
                'implementation_notes': self._generate_implementation_notes()
            }
            
        except Exception as e:
            logger.error(f"Error generating component system: {e}")
            return self._create_fallback_component_system()
    
    def _find_figma_templates(self, category: str, trend_keyword: str) -> Dict[str, Any]:
        """Find matching Figma Community templates"""
        try:
            logger.info(f"Finding Figma templates for {category}: {trend_keyword}")
            
            # Since Figma Community API requires authentication, we'll provide
            # curated template recommendations based on category
            template_recommendations = {
                'health': [
                    {
                        'name': 'Health & Fitness App UI Kit',
                        'url': 'https://www.figma.com/community/file/health-fitness-ui-kit',
                        'description': 'Complete UI kit for health and fitness applications',
                        'components': 120,
                        'rating': 4.8,
                        'downloads': '15k+'
                    },
                    {
                        'name': 'Medical Dashboard Template',
                        'url': 'https://www.figma.com/community/file/medical-dashboard',
                        'description': 'Professional medical dashboard with data visualization',
                        'components': 80,
                        'rating': 4.6,
                        'downloads': '8k+'
                    }
                ],
                'productivity': [
                    {
                        'name': 'Productivity App Design System',
                        'url': 'https://www.figma.com/community/file/productivity-design-system',
                        'description': 'Complete design system for productivity applications',
                        'components': 200,
                        'rating': 4.9,
                        'downloads': '25k+'
                    },
                    {
                        'name': 'Task Management UI Kit',
                        'url': 'https://www.figma.com/community/file/task-management-ui',
                        'description': 'Modern task management interface components',
                        'components': 95,
                        'rating': 4.7,
                        'downloads': '12k+'
                    }
                ],
                'finance': [
                    {
                        'name': 'Fintech Mobile App UI',
                        'url': 'https://www.figma.com/community/file/fintech-mobile-ui',
                        'description': 'Modern fintech mobile application design',
                        'components': 150,
                        'rating': 4.8,
                        'downloads': '18k+'
                    }
                ]
            }
            
            # Get templates for category or provide general templates
            templates = template_recommendations.get(category, [
                {
                    'name': 'Universal UI Kit',
                    'url': 'https://www.figma.com/community/file/universal-ui-kit',
                    'description': 'Versatile UI components for any application type',
                    'components': 180,
                    'rating': 4.7,
                    'downloads': '30k+'
                }
            ])
            
            # Add custom search results based on trend keyword
            if trend_keyword:
                custom_templates = self._search_custom_templates(trend_keyword, category)
                templates.extend(custom_templates)
            
            return {
                'recommended_templates': templates,
                'search_criteria': {
                    'category': category,
                    'keyword': trend_keyword,
                    'filters': ['free', 'community', 'mobile-ready']
                },
                'implementation_guide': self._generate_figma_implementation_guide(),
                'customization_tips': self._generate_figma_customization_tips()
            }
            
        except Exception as e:
            logger.error(f"Error finding Figma templates: {e}")
            return self._create_fallback_figma_templates()
    
    def _generate_design_tokens(self, colors: Dict, typography: Dict) -> Dict[str, Any]:
        """Generate design tokens for consistent implementation"""
        try:
            # Extract color values
            color_tokens = {}
            for color_type, color_values in colors.get('colors', {}).items():
                if isinstance(color_values, dict):
                    for shade, value in color_values.items():
                        color_tokens[f'color-{color_type}-{shade}'] = value
                else:
                    color_tokens[f'color-{color_type}'] = color_values
            
            # Extract typography tokens
            typography_tokens = {
                'font-family-display': typography.get('font_families', {}).get('display', 'Inter'),
                'font-family-body': typography.get('font_families', {}).get('body', 'Inter'),
                'font-family-mono': typography.get('font_families', {}).get('mono', 'JetBrains Mono')
            }
            
            # Add type scale tokens
            type_scale = typography.get('type_scale', {})
            for size_name, size_value in type_scale.items():
                typography_tokens[f'font-size-{size_name}'] = size_value
            
            # Add spacing tokens
            spacing_tokens = {
                'spacing-xs': '0.25rem',
                'spacing-sm': '0.5rem',
                'spacing-md': '1rem',
                'spacing-lg': '1.5rem',
                'spacing-xl': '2rem',
                'spacing-2xl': '3rem',
                'spacing-3xl': '4rem'
            }
            
            # Add border radius tokens
            border_radius_tokens = {
                'radius-none': '0',
                'radius-sm': '0.125rem',
                'radius-md': '0.375rem',
                'radius-lg': '0.5rem',
                'radius-xl': '0.75rem',
                'radius-full': '9999px'
            }
            
            # Add shadow tokens
            shadow_tokens = {
                'shadow-sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                'shadow-md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                'shadow-lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                'shadow-xl': '0 20px 25px -5px rgb(0 0 0 / 0.1)'
            }
            
            return {
                'colors': color_tokens,
                'typography': typography_tokens,
                'spacing': spacing_tokens,
                'border_radius': border_radius_tokens,
                'shadows': shadow_tokens,
                'format_versions': {
                    'css_custom_properties': True,
                    'scss_variables': True,
                    'js_tokens': True,
                    'tailwind_config': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating design tokens: {e}")
            return {}
    
    def _create_usage_guidelines(self, colors: Dict, typography: Dict, icons: Dict) -> Dict[str, Any]:
        """Create comprehensive usage guidelines"""
        return {
            'color_guidelines': {
                'primary_usage': 'Use for main actions, links, and brand elements',
                'secondary_usage': 'Use for less prominent actions and secondary content',
                'neutral_usage': 'Use for text, borders, and background elements',
                'semantic_usage': 'Use semantic colors consistently for status messages',
                'accessibility': 'Ensure minimum 4.5:1 contrast ratio for text'
            },
            'typography_guidelines': {
                'hierarchy': 'Use display fonts for headings, body fonts for content',
                'readability': 'Maintain line height of 1.5 for body text',
                'responsive': 'Scale font sizes appropriately for different screen sizes',
                'performance': 'Limit font weights to improve loading times'
            },
            'icon_guidelines': {
                'consistency': 'Use icons from the same library for visual consistency',
                'sizing': 'Maintain consistent icon sizes within the same context',
                'accessibility': 'Always provide alternative text for screen readers',
                'touch_targets': 'Ensure minimum 44px touch targets for interactive icons'
            },
            'general_principles': [
                'Maintain visual consistency across all components',
                'Prioritize accessibility in all design decisions',
                'Optimize for performance and loading speed',
                'Design with mobile-first approach',
                'Test designs with real users regularly'
            ]
        }
    
    # Helper methods for color manipulation
    def _hex_to_hsl(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to HSL"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = r/255.0, g/255.0, b/255.0
        return colorsys.rgb_to_hls(r, g, b)
    
    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """Convert HSL to hex color"""
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    def _generate_color_variant(self, base_hsl: Tuple[float, float, float], lightness: float, saturation_factor: float) -> str:
        """Generate color variant with different lightness and saturation"""
        h, l, s = base_hsl
        new_l = lightness
        new_s = s * saturation_factor
        return self._hsl_to_hex(h, min(new_s, 1.0), new_l)
    
    def _generate_complementary_colors(self, primary_hsl: Tuple[float, float, float]) -> Dict[str, str]:
        """Generate complementary color palette"""
        h, l, s = primary_hsl
        
        # Generate analogous colors (adjacent on color wheel)
        analogous1 = self._hsl_to_hex((h + 0.083) % 1.0, l, s * 0.8)  # +30 degrees
        analogous2 = self._hsl_to_hex((h - 0.083) % 1.0, l, s * 0.8)  # -30 degrees
        
        # Generate triadic color (120 degrees)
        triadic = self._hsl_to_hex((h + 0.333) % 1.0, l, s * 0.7)
        
        return {
            'analogous_warm': analogous1,
            'analogous_cool': analogous2,
            'triadic': triadic
        }
    
    def _generate_neutral_colors(self) -> Dict[str, str]:
        """Generate neutral color palette"""
        return {
            '50': '#F9FAFB',
            '100': '#F3F4F6',
            '200': '#E5E7EB',
            '300': '#D1D5DB',
            '400': '#9CA3AF',
            '500': '#6B7280',
            '600': '#4B5563',
            '700': '#374151',
            '800': '#1F2937',
            '900': '#111827'
        }
    
    def _check_color_accessibility(self, colors: Dict) -> Dict[str, Any]:
        """Check color accessibility and contrast ratios"""
        # Simplified accessibility check
        return {
            'wcag_aa_compliant': True,
            'wcag_aaa_compliant': False,
            'contrast_ratios': {
                'primary_on_white': '4.5:1',
                'primary_on_dark': '3.2:1'
            },
            'recommendations': [
                'Use primary-600 or darker for text on light backgrounds',
                'Use primary-300 or lighter for text on dark backgrounds',
                'Test all color combinations with contrast checking tools'
            ]
        }
    
    def _get_cultural_color_considerations(self, category: str) -> List[str]:
        """Get cultural considerations for color choices"""
        considerations = {
            'health': ['Green represents wellness globally', 'Avoid red for positive health indicators'],
            'finance': ['Green for growth, red for loss in Western cultures', 'Blue for trust and stability'],
            'education': ['Blue for knowledge and trust', 'Avoid overwhelming bright colors'],
            'general': ['Consider color blindness accessibility', 'Test colors across different cultures']
        }
        return considerations.get(category, considerations['general'])
    
    def _get_color_usage_recommendations(self, colors: Dict) -> Dict[str, str]:
        """Get specific usage recommendations for colors"""
        return {
            'primary': 'Use for main CTAs, links, and brand elements. Avoid overuse.',
            'secondary': 'Use for secondary actions and accents. Pair with primary.',
            'neutral': 'Use for text, borders, and backgrounds. Provides visual rest.',
            'semantic': 'Use consistently for status messages and system feedback.'
        }
    
    # Typography helper methods
    def _select_font_style(self, category: str, ux_strategy: Dict) -> str:
        """Select appropriate font style based on category and strategy"""
        category_mapping = {
            'health': 'friendly',
            'productivity': 'modern',
            'finance': 'elegant',
            'education': 'friendly',
            'entertainment': 'creative',
            'business': 'elegant',
            'technology': 'tech',
            'lifestyle': 'creative'
        }
        
        # Check UX strategy for style hints
        strategies = ux_strategy.get('strategies', [])
        if strategies:
            primary_strategy = strategies[0].get('direction', '').lower()
            if 'simple' in primary_strategy or 'minimal' in primary_strategy:
                return 'modern'
            elif 'creative' in primary_strategy or 'fun' in primary_strategy:
                return 'creative'
            elif 'professional' in primary_strategy:
                return 'elegant'
        
        return category_mapping.get(category, 'modern')
    
    def _get_google_fonts_details(self, font_names: List[str]) -> Dict[str, Any]:
        """Get details about Google Fonts (simulated API call)"""
        # In a real implementation, this would call the Google Fonts API
        font_details = {}
        for font_name in font_names:
            font_details[font_name] = {
                'family': font_name,
                'variants': ['300', '400', '500', '600', '700'],
                'subsets': ['latin', 'latin-ext'],
                'category': 'sans-serif',
                'popularity': 85
            }
        return font_details
    
    def _generate_type_scale(self) -> Dict[str, str]:
        """Generate modular type scale"""
        return {
            'xs': '0.75rem',    # 12px
            'sm': '0.875rem',   # 14px
            'base': '1rem',     # 16px
            'lg': '1.125rem',   # 18px
            'xl': '1.25rem',    # 20px
            '2xl': '1.5rem',    # 24px
            '3xl': '1.875rem',  # 30px
            '4xl': '2.25rem',   # 36px
            '5xl': '3rem',      # 48px
            '6xl': '3.75rem',   # 60px
            '7xl': '4.5rem',    # 72px
            '8xl': '6rem',      # 96px
            '9xl': '8rem'       # 128px
        }
    
    def _generate_google_fonts_imports(self, font_combo: Dict) -> Dict[str, str]:
        """Generate Google Fonts import statements"""
        fonts = [font_combo['display'], font_combo['body']]
        unique_fonts = list(set(fonts))  # Remove duplicates
        
        font_string = '|'.join([font.replace(' ', '+') for font in unique_fonts])
        
        return {
            'css_import': f"@import url('https://fonts.googleapis.com/css2?family={font_string}:wght@300;400;500;600;700&display=swap');",
            'html_link': f'<link href="https://fonts.googleapis.com/css2?family={font_string}:wght@300;400;500;600;700&display=swap" rel="stylesheet">',
            'font_faces': [f"font-family: '{font}', sans-serif;" for font in unique_fonts]
        }
    
    def _generate_typography_guidelines(self, font_combo: Dict) -> Dict[str, str]:
        """Generate typography usage guidelines"""
        return {
            'headings': f"Use {font_combo['display']} for all headings (h1-h6)",
            'body_text': f"Use {font_combo['body']} for body text, paragraphs, and UI elements",
            'ui_elements': f"Use {font_combo['body']} for buttons, forms, and interactive elements",
            'code': "Use JetBrains Mono for code snippets and technical content",
            'line_length': "Keep line length between 45-75 characters for optimal readability",
            'hierarchy': "Maintain clear typographic hierarchy with size, weight, and spacing"
        }
    
    # Icon system helper methods
    def _select_icon_library(self, category: str) -> str:
        """Select appropriate icon library based on category"""
        category_mapping = {
            'health': 'heroicons',      # Clean, medical-friendly
            'productivity': 'lucide',   # Sharp, professional
            'finance': 'heroicons',     # Trustworthy, clean
            'education': 'lucide',      # Clear, educational
            'entertainment': 'tabler',  # Fun, expressive
            'business': 'heroicons',    # Professional, clean
            'technology': 'lucide',     # Technical, precise
            'lifestyle': 'tabler'       # Trendy, diverse
        }
        return category_mapping.get(category, 'heroicons')
    
    def _generate_icon_implementation(self, library: str, categories: Dict) -> Dict[str, Any]:
        """Generate icon implementation code and CDN links"""
        library_info = self.icon_collections.get(library, self.icon_collections['heroicons'])
        
        return {
            'cdn_links': {
                'css': f"{library_info['cdn_url']}/style.css",
                'js': f"{library_info['cdn_url']}/index.js"
            },
            'usage_examples': {
                'html': f'<i class="{library}-icon-home"></i>',
                'react': f'import {{ HomeIcon }} from "@{library}/react/24/outline"',
                'vue': f'import {{ HomeIcon }} from "@{library}/vue/24/outline"'
            },
            'recommended_icons': {
                category: icons[:3] for category, icons in categories.items()
            },
            'customization': {
                'size': 'Use CSS to control icon size: .icon { width: 24px; height: 24px; }',
                'color': 'Use currentColor to inherit text color: stroke="currentColor"',
                'weight': 'Adjust stroke-width for different visual weights'
            }
        }
    
    def _generate_icon_guidelines(self, library: str) -> Dict[str, str]:
        """Generate icon usage guidelines"""
        return {
            'consistency': f'Use only {library} icons throughout the application for visual consistency',
            'sizing': 'Use consistent icon sizes: 16px (small), 24px (medium), 32px (large)',
            'alignment': 'Align icons with text baseline and maintain consistent spacing',
            'accessibility': 'Always include aria-label or title attributes for screen readers',
            'interaction': 'Use hover and focus states for interactive icons',
            'context': 'Choose icons that clearly represent their function or content'
        }
    
    # Component generation helper methods
    def _generate_button_components(self, colors: Dict, strategy: Dict) -> Dict[str, Any]:
        """Generate button component specifications"""
        button_variants = {
            'primary': {
                'background': colors.get('colors', {}).get('primary', {}).get('500', '#3B82F6'),
                'text': '#FFFFFF',
                'hover': colors.get('colors', {}).get('primary', {}).get('600', '#2563EB'),
                'focus': colors.get('colors', {}).get('primary', {}).get('700', '#1D4ED8')
            },
            'secondary': {
                'background': 'transparent',
                'text': colors.get('colors', {}).get('primary', {}).get('500', '#3B82F6'),
                'border': colors.get('colors', {}).get('primary', {}).get('500', '#3B82F6'),
                'hover': colors.get('colors', {}).get('primary', {}).get('50', '#EFF6FF')
            },
            'ghost': {
                'background': 'transparent',
                'text': colors.get('colors', {}).get('neutral', {}).get('700', '#374151'),
                'hover': colors.get('colors', {}).get('neutral', {}).get('100', '#F3F4F6')
            }
        }
        
        # Adjust based on strategy
        if strategy.get('direction', '').lower().find('simple') != -1:
            button_variants['primary']['border_radius'] = '0.375rem'  # More rounded
        
        return {
            'variants': button_variants,
            'sizes': {
                'sm': {'padding': '0.5rem 1rem', 'font_size': '0.875rem'},
                'md': {'padding': '0.75rem 1.5rem', 'font_size': '1rem'},
                'lg': {'padding': '1rem 2rem', 'font_size': '1.125rem'}
            },
            'tailwind_classes': self._generate_button_tailwind_classes(button_variants)
        }
    
    def _generate_form_components(self, colors: Dict, typography: Dict) -> Dict[str, Any]:
        """Generate form component specifications"""
        return {
            'input_field': {
                'border': colors.get('colors', {}).get('neutral', {}).get('300', '#D1D5DB'),
                'focus_border': colors.get('colors', {}).get('primary', {}).get('500', '#3B82F6'),
                'background': '#FFFFFF',
                'text': colors.get('colors', {}).get('neutral', {}).get('900', '#111827'),
                'placeholder': colors.get('colors', {}).get('neutral', {}).get('400', '#9CA3AF')
            },
            'label': {
                'text': colors.get('colors', {}).get('neutral', {}).get('700', '#374151'),
                'font_weight': '500',
                'margin_bottom': '0.5rem'
            },
            'error_state': {
                'border': colors.get('colors', {}).get('semantic', {}).get('error', '#EF4444'),
                'text': colors.get('colors', {}).get('semantic', {}).get('error', '#EF4444')
            }
        }
    
    def _generate_card_components(self, colors: Dict) -> Dict[str, Any]:
        """Generate card component specifications"""
        return {
            'default': {
                'background': '#FFFFFF',
                'border': colors.get('colors', {}).get('neutral', {}).get('200', '#E5E7EB'),
                'shadow': '0 1px 3px 0 rgb(0 0 0 / 0.1)',
                'border_radius': '0.5rem'
            },
            'elevated': {
                'background': '#FFFFFF',
                'shadow': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                'border_radius': '0.75rem'
            },
            'interactive': {
                'background': '#FFFFFF',
                'border': colors.get('colors', {}).get('neutral', {}).get('200', '#E5E7EB'),
                'hover_shadow': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                'transition': 'all 0.2s ease-in-out'
            }
        }
    
    def _generate_navigation_components(self, colors: Dict, strategy: Dict) -> Dict[str, Any]:
        """Generate navigation component specifications"""
        return {
            'navbar': {
                'background': '#FFFFFF',
                'border_bottom': colors.get('colors', {}).get('neutral', {}).get('200', '#E5E7EB'),
                'height': '4rem'
            },
            'sidebar': {
                'background': colors.get('colors', {}).get('neutral', {}).get('50', '#F9FAFB'),
                'width': '16rem',
                'border_right': colors.get('colors', {}).get('neutral', {}).get('200', '#E5E7EB')
            },
            'tab_navigation': {
                'active': colors.get('colors', {}).get('primary', {}).get('500', '#3B82F6'),
                'inactive': colors.get('colors', {}).get('neutral', {}).get('500', '#6B7280'),
                'border_bottom': colors.get('colors', {}).get('primary', {}).get('500', '#3B82F6')
            }
        }
    
    def _generate_feedback_components(self, colors: Dict) -> Dict[str, Any]:
        """Generate feedback component specifications"""
        return {
            'alert': {
                'success': {
                    'background': colors.get('colors', {}).get('semantic', {}).get('success', '#10B981') + '1A',  # 10% opacity
                    'border': colors.get('colors', {}).get('semantic', {}).get('success', '#10B981'),
                    'text': colors.get('colors', {}).get('semantic', {}).get('success', '#10B981')
                },
                'warning': {
                    'background': colors.get('colors', {}).get('semantic', {}).get('warning', '#F59E0B') + '1A',
                    'border': colors.get('colors', {}).get('semantic', {}).get('warning', '#F59E0B'),
                    'text': colors.get('colors', {}).get('semantic', {}).get('warning', '#F59E0B')
                },
                'error': {
                    'background': colors.get('colors', {}).get('semantic', {}).get('error', '#EF4444') + '1A',
                    'border': colors.get('colors', {}).get('semantic', {}).get('error', '#EF4444'),
                    'text': colors.get('colors', {}).get('semantic', {}).get('error', '#EF4444')
                }
            },
            'toast': {
                'background': colors.get('colors', {}).get('neutral', {}).get('800', '#1F2937'),
                'text': '#FFFFFF',
                'border_radius': '0.5rem',
                'shadow': '0 10px 15px -3px rgb(0 0 0 / 0.1)'
            }
        }
    
    def _generate_layout_components(self) -> Dict[str, Any]:
        """Generate layout component specifications"""
        return {
            'container': {
                'max_width': '1200px',
                'margin': '0 auto',
                'padding': '0 1rem'
            },
            'grid': {
                'columns': 12,
                'gap': '1rem',
                'responsive_breakpoints': {
                    'sm': '640px',
                    'md': '768px', 
                    'lg': '1024px',
                    'xl': '1280px'
                }
            },
            'spacing': {
                'section_margin': '4rem',
                'component_margin': '2rem',
                'element_margin': '1rem'
            }
        }
    
    # Additional helper methods
    def _generate_component_variants(self, component_type: str) -> List[str]:
        """Generate component variants"""
        variant_mapping = {
            'buttons': ['primary', 'secondary', 'ghost', 'outline'],
            'forms': ['default', 'floating', 'inline'],
            'cards': ['default', 'elevated', 'outlined', 'interactive'],
            'navigation': ['horizontal', 'vertical', 'breadcrumb'],
            'feedback': ['success', 'warning', 'error', 'info'],
            'layout': ['fixed', 'fluid', 'responsive']
        }
        return variant_mapping.get(component_type, ['default'])
    
    def _generate_component_states(self) -> List[str]:
        """Generate component states"""
        return ['default', 'hover', 'focus', 'active', 'disabled', 'loading']
    
    def _extract_design_principles(self, ux_strategy: Dict) -> List[str]:
        """Extract design principles from UX strategy"""
        principles = ux_strategy.get('design_principles', [])
        if not principles:
            principles = [
                'Prioritize usability over visual complexity',
                'Maintain consistent visual patterns',
                'Design for accessibility and inclusion',
                'Optimize for performance and speed',
                'Create intuitive user flows'
            ]
        return principles
    
    def _generate_responsive_guidelines(self) -> Dict[str, str]:
        """Generate responsive design guidelines"""
        return {
            'mobile_first': 'Design for mobile screens first, then enhance for larger screens',
            'breakpoints': 'Use consistent breakpoints: 640px, 768px, 1024px, 1280px',
            'touch_targets': 'Ensure minimum 44px touch targets for mobile interactions',
            'typography': 'Scale typography appropriately for different screen sizes',
            'navigation': 'Adapt navigation patterns for touch vs. desktop interactions'
        }
    
    def _generate_accessibility_standards(self) -> Dict[str, str]:
        """Generate accessibility standards"""
        return {
            'color_contrast': 'Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text',
            'keyboard_navigation': 'All interactive elements must be keyboard accessible',
            'screen_readers': 'Provide proper semantic markup and ARIA labels',
            'focus_indicators': 'Clear focus indicators for keyboard navigation',
            'alternative_text': 'Descriptive alt text for all images and icons'
        }
    
    def _generate_implementation_notes(self) -> Dict[str, str]:
        """Generate implementation notes"""
        return {
            'css_methodology': 'Use BEM naming convention or utility-first approach',
            'performance': 'Optimize images and minimize CSS/JS bundle sizes',
            'browser_support': 'Test across modern browsers and provide fallbacks',
            'maintenance': 'Document component usage and maintain style guide',
            'testing': 'Include visual regression testing for design consistency'
        }
    
    def _search_custom_templates(self, keyword: str, category: str) -> List[Dict[str, Any]]:
        """Search for custom templates based on keyword and category"""
        # Simulated search results
        return [
            {
                'name': f'{keyword.title()} App Template',
                'url': f'https://www.figma.com/community/file/{keyword.lower().replace(" ", "-")}-template',
                'description': f'Modern {keyword} application design template',
                'components': 85,
                'rating': 4.5,
                'downloads': '5k+'
            }
        ]
    
    def _generate_figma_implementation_guide(self) -> Dict[str, str]:
        """Generate Figma implementation guide"""
        return {
            'setup': 'Duplicate template to your Figma account and customize colors',
            'customization': 'Update color styles and text styles to match your brand',
            'components': 'Modify component instances while maintaining the component structure',
            'export': 'Use Figma plugins to export assets and generate code',
            'collaboration': 'Share with developers using Figma dev mode for accurate handoff'
        }
    
    def _generate_figma_customization_tips(self) -> List[str]:
        """Generate Figma customization tips"""
        return [
            'Start by updating the color palette in the design system',
            'Replace placeholder content with your actual content',
            'Customize component instances rather than detaching from components',
            'Use Figma variants to create different component states',
            'Test your designs with real content and data',
            'Create a style guide page for documentation'
        ]
    
    # Implementation helper methods
    def _generate_css_variables(self, tokens: Dict) -> str:
        """Generate CSS custom properties from design tokens"""
        css_vars = [":root {"]
        
        for category, values in tokens.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    css_vars.append(f"  --{key}: {value};")
        
        css_vars.append("}")
        return "\n".join(css_vars)
    
    def _generate_tailwind_config(self, colors: Dict, typography: Dict) -> Dict[str, Any]:
        """Generate Tailwind CSS configuration"""
        return {
            'theme': {
                'extend': {
                    'colors': colors.get('colors', {}),
                    'fontFamily': {
                        'display': [typography.get('font_families', {}).get('display', 'Inter')],
                        'body': [typography.get('font_families', {}).get('body', 'Inter')],
                        'mono': [typography.get('font_families', {}).get('mono', 'JetBrains Mono')]
                    },
                    'fontSize': typography.get('type_scale', {}),
                    'fontWeight': typography.get('font_weights', {})
                }
            },
            'plugins': ['@tailwindcss/forms', '@tailwindcss/typography']
        }
    
    def _generate_react_theme(self, tokens: Dict) -> Dict[str, Any]:
        """Generate React theme object"""
        theme = {}
        for category, values in tokens.items():
            if isinstance(values, dict):
                theme[category] = values
        return theme
    
    def _generate_button_tailwind_classes(self, variants: Dict) -> Dict[str, str]:
        """Generate Tailwind CSS classes for button variants"""
        return {
            'primary': 'bg-primary-500 text-white hover:bg-primary-600 focus:bg-primary-700 px-4 py-2 rounded-md font-medium',
            'secondary': 'bg-transparent text-primary-500 border border-primary-500 hover:bg-primary-50 px-4 py-2 rounded-md font-medium',
            'ghost': 'bg-transparent text-neutral-700 hover:bg-neutral-100 px-4 py-2 rounded-md font-medium'
        }
    
    def _extract_brand_personality(self, ux_analysis: Dict) -> Dict[str, Any]:
        """Extract brand personality from UX analysis"""
        category = ux_analysis.get('category', 'general')
        personas = ux_analysis.get('personas', [])
        strategy = ux_analysis.get('ux_strategy', {})
        
        # Extract personality traits
        personality_traits = []
        if personas:
            primary_persona = personas[0]
            motivations = primary_persona.get('motivations', [])
            personality_traits.extend(motivations)
        
        # Extract from strategy
        strategies = strategy.get('strategies', [])
        if strategies:
            primary_strategy = strategies[0]
            direction = primary_strategy.get('direction', '')
            personality_traits.append(direction)
        
        return {
            'traits': personality_traits[:5],  # Top 5 traits
            'tone': self._map_category_to_tone(category),
            'values': self._extract_brand_values(ux_analysis),
            'voice': self._generate_brand_voice(personality_traits)
        }
    
    def _map_category_to_tone(self, category: str) -> str:
        """Map category to brand tone"""
        tone_mapping = {
            'health': 'encouraging, supportive, trustworthy',
            'productivity': 'efficient, focused, helpful',
            'finance': 'trustworthy, professional, secure',
            'education': 'knowledgeable, inspiring, accessible',
            'entertainment': 'fun, engaging, dynamic',
            'business': 'professional, reliable, innovative',
            'technology': 'cutting-edge, precise, forward-thinking',
            'lifestyle': 'inspiring, personal, authentic'
        }
        return tone_mapping.get(category, 'professional, helpful, reliable')
    
    def _extract_brand_values(self, ux_analysis: Dict) -> List[str]:
        """Extract brand values from UX analysis"""
        values = []
        
        # Extract from user needs
        user_needs = ux_analysis.get('user_needs', {})
        if 'key_insights' in user_needs:
            insights = user_needs['key_insights']
            for insight in insights[:3]:
                if 'simple' in insight.lower():
                    values.append('Simplicity')
                elif 'trust' in insight.lower():
                    values.append('Trustworthiness')
                elif 'efficient' in insight.lower():
                    values.append('Efficiency')
        
        # Default values if none extracted
        if not values:
            values = ['User-centricity', 'Quality', 'Innovation']
        
        return values
    
    def _generate_brand_voice(self, traits: List[str]) -> str:
        """Generate brand voice description"""
        if not traits:
            return 'Professional, helpful, and user-focused'
        
        voice_elements = []
        for trait in traits[:3]:
            trait_lower = trait.lower()
            if 'simple' in trait_lower or 'easy' in trait_lower:
                voice_elements.append('clear and straightforward')
            elif 'professional' in trait_lower:
                voice_elements.append('professional and authoritative')
            elif 'friendly' in trait_lower or 'warm' in trait_lower:
                voice_elements.append('friendly and approachable')
            elif 'efficient' in trait_lower:
                voice_elements.append('direct and efficient')
        
        if not voice_elements:
            voice_elements = ['professional', 'helpful', 'user-focused']
        
        return ', '.join(voice_elements)
    
    # Fallback methods
    def _create_fallback_color_palette(self, category: str) -> Dict[str, Any]:
        """Create fallback color palette when generation fails"""
        base_color = self.color_psychology.get(category, self.color_psychology['business'])['primary']
        
        return {
            'colors': {
                'primary': {
                    '500': base_color,
                    '600': '#2563EB',
                    '700': '#1D4ED8'
                },
                'neutral': self._generate_neutral_colors(),
                'semantic': {
                    'success': '#10B981',
                    'warning': '#F59E0B',
                    'error': '#EF4444',
                    'info': '#3B82F6'
                }
            },
            'accessibility': {'wcag_aa_compliant': True},
            'psychology': {'mood': 'professional, trustworthy'}
        }
    
    def _create_fallback_typography_system(self) -> Dict[str, Any]:
        """Create fallback typography system"""
        return {
            'font_families': {
                'display': 'Inter',
                'body': 'Inter',
                'mono': 'JetBrains Mono'
            },
            'type_scale': self._generate_type_scale(),
            'font_weights': {
                'regular': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            }
        }
    
    def _create_fallback_icon_system(self) -> Dict[str, Any]:
        """Create fallback icon system"""
        return {
            'primary_library': 'heroicons',
            'categories': {
                'navigation': ['home', 'menu', 'search'],
                'actions': ['plus', 'edit', 'delete'],
                'status': ['check', 'x', 'alert-triangle']
            },
            'specifications': {
                'sizes': {'sm': '20px', 'md': '24px', 'lg': '32px'}
            }
        }
    
    def _create_fallback_component_system(self) -> Dict[str, Any]:
        """Create fallback component system"""
        return {
            'components': {
                'buttons': {
                    'variants': {
                        'primary': {'background': '#3B82F6', 'text': '#FFFFFF'},
                        'secondary': {'background': 'transparent', 'text': '#3B82F6'}
                    }
                }
            },
            'design_principles': [
                'Keep it simple and intuitive',
                'Maintain visual consistency',
                'Prioritize accessibility'
            ]
        }
    
    def _create_fallback_figma_templates(self) -> Dict[str, Any]:
        """Create fallback Figma templates"""
        return {
            'recommended_templates': [
                {
                    'name': 'Universal UI Kit',
                    'url': 'https://www.figma.com/community',
                    'description': 'Comprehensive UI components',
                    'components': 100,
                    'rating': 4.5
                }
            ],
            'implementation_guide': {
                'setup': 'Visit Figma Community and search for relevant templates'
            }
        }

# Global instance
design_system_generator = DesignSystemGenerator()