import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..utils.config import config
from ..utils.api_clients import api_manager

logger = logging.getLogger(__name__)

class DesignGenerator:
    def __init__(self):
        self.enabled = config.is_agent_enabled('design_generator')
        self.output_format = config.get('agents.design_generator.output_format', 'markdown')
        
        if not self.enabled:
            logger.info("Design Generator agent is disabled")
            return
        
        self.openai_client = api_manager.get_client('openai')
        self.supabase_client = api_manager.get_client('supabase')
    
    def generate_ui_wireframes(self, app_idea: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Design Generator agent is disabled"}
        
        try:
            logger.info(f"Generating UI wireframes for: {app_idea.get('title', 'Unknown app')}")
            
            app_category = app_idea.get('category', 'general')
            core_features = app_idea.get('core_features', [])
            target_users = app_idea.get('target_market', 'general users')
            
            wireframes = {
                'onboarding_flow': self._generate_onboarding_wireframe(target_users),
                'main_dashboard': self._generate_dashboard_wireframe(core_features, app_category),
                'feature_screens': self._generate_feature_wireframes(core_features),
                'settings_screen': self._generate_settings_wireframe(),
                'navigation_structure': self._generate_navigation_structure(core_features)
            }
            
            design_system = self._generate_design_system(app_category, target_users)
            
            return {
                'app_idea': app_idea.get('title', 'Unknown'),
                'wireframes': wireframes,
                'design_system': design_system,
                'user_flow': self._generate_user_flow(core_features),
                'responsive_considerations': self._generate_responsive_guidelines(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating UI wireframes: {e}")
            return {"error": str(e)}
    
    def generate_user_experience_flow(self, app_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Design Generator agent is disabled"}
        
        try:
            logger.info("Generating user experience flow...")
            
            user_journeys = self._create_user_journeys(app_features)
            interaction_patterns = self._define_interaction_patterns(app_features)
            accessibility_guidelines = self._generate_accessibility_guidelines()
            
            return {
                'user_journeys': user_journeys,
                'interaction_patterns': interaction_patterns,
                'accessibility_guidelines': accessibility_guidelines,
                'usability_principles': self._define_usability_principles(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating UX flow: {e}")
            return {"error": str(e)}
    
    def generate_visual_design_concepts(self, app_idea: Dict[str, Any], brand_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Design Generator agent is disabled"}
        
        try:
            logger.info("Generating visual design concepts...")
            
            if brand_preferences is None:
                brand_preferences = {}
            
            color_schemes = self._generate_color_schemes(app_idea.get('category'), brand_preferences)
            typography_system = self._generate_typography_system(app_idea.get('target_market'))
            iconography_style = self._generate_iconography_guidelines(app_idea.get('category'))
            layout_principles = self._generate_layout_principles()
            
            return {
                'color_schemes': color_schemes,
                'typography_system': typography_system,
                'iconography_style': iconography_style,
                'layout_principles': layout_principles,
                'brand_guidelines': self._generate_brand_guidelines(app_idea, brand_preferences),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating visual design concepts: {e}")
            return {"error": str(e)}
    
    def generate_component_library(self, design_system: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Design Generator agent is disabled"}
        
        try:
            logger.info("Generating component library...")
            
            basic_components = self._generate_basic_components()
            form_components = self._generate_form_components()
            navigation_components = self._generate_navigation_components()
            data_display_components = self._generate_data_display_components()
            feedback_components = self._generate_feedback_components()
            
            component_library = {
                'basic': basic_components,
                'forms': form_components,
                'navigation': navigation_components,
                'data_display': data_display_components,
                'feedback': feedback_components
            }
            
            return {
                'component_library': component_library,
                'usage_guidelines': self._generate_component_usage_guidelines(),
                'code_examples': self._generate_component_code_examples(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating component library: {e}")
            return {"error": str(e)}
    
    def generate_prototype_specifications(self, wireframes: Dict[str, Any], visual_design: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"error": "Design Generator agent is disabled"}
        
        try:
            logger.info("Generating prototype specifications...")
            
            prototype_structure = self._create_prototype_structure(wireframes)
            interaction_specifications = self._define_interaction_specifications(wireframes)
            animation_guidelines = self._generate_animation_guidelines()
            responsive_breakpoints = self._define_responsive_breakpoints()
            
            return {
                'prototype_structure': prototype_structure,
                'interaction_specifications': interaction_specifications,
                'animation_guidelines': animation_guidelines,
                'responsive_breakpoints': responsive_breakpoints,
                'testing_checklist': self._generate_design_testing_checklist(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating prototype specifications: {e}")
            return {"error": str(e)}
    
    def _generate_onboarding_wireframe(self, target_users: str) -> Dict[str, Any]:
        return {
            'welcome_screen': {
                'elements': ['App logo', 'Welcome message', 'Get started button'],
                'layout': 'Centered vertical layout',
                'interactions': ['Tap to continue']
            },
            'feature_introduction': {
                'elements': ['Feature highlights', 'Progress indicators', 'Skip option'],
                'layout': 'Swipeable cards',
                'interactions': ['Swipe to navigate', 'Skip to main app']
            },
            'account_setup': {
                'elements': ['Email input', 'Password creation', 'Terms acceptance'],
                'layout': 'Form layout with validation',
                'interactions': ['Form validation', 'Create account']
            },
            'personalization': {
                'elements': ['Preferences selection', 'Goals setting', 'Notification preferences'],
                'layout': 'Step-by-step wizard',
                'interactions': ['Multi-step form', 'Save preferences']
            }
        }
    
    def _generate_dashboard_wireframe(self, core_features: List, app_category: str) -> Dict[str, Any]:
        dashboard_layouts = {
            'productivity': {
                'header': ['User avatar', 'Notifications', 'Search'],
                'main_content': ['Quick actions', 'Recent items', 'Progress overview'],
                'sidebar': ['Navigation menu', 'Filters', 'Settings link']
            },
            'social': {
                'header': ['Logo', 'Search', 'Messages', 'Profile'],
                'main_content': ['Content feed', 'Stories', 'Trending topics'],
                'sidebar': ['Friends list', 'Groups', 'Events']
            },
            'utility': {
                'header': ['Menu toggle', 'Page title', 'Help'],
                'main_content': ['Tool grid', 'Recent activity', 'Quick access'],
                'sidebar': ['Tool categories', 'Favorites', 'History']
            }
        }
        
        return dashboard_layouts.get(app_category, dashboard_layouts['utility'])
    
    def _generate_feature_wireframes(self, core_features: List) -> Dict[str, Any]:
        wireframes = {}
        
        for feature in core_features[:5]:
            feature_name = feature.get('name', 'Unknown Feature') if isinstance(feature, dict) else str(feature)
            wireframes[feature_name.lower().replace(' ', '_')] = {
                'header': ['Back button', 'Feature title', 'More options'],
                'content': ['Main feature interface', 'Action buttons', 'Help text'],
                'footer': ['Primary action', 'Secondary actions']
            }
        
        return wireframes
    
    def _generate_settings_wireframe(self) -> Dict[str, Any]:
        return {
            'profile_section': {
                'elements': ['Profile picture', 'Name', 'Email', 'Edit button'],
                'layout': 'Card layout'
            },
            'preferences_section': {
                'elements': ['Notification settings', 'Privacy settings', 'Theme selection'],
                'layout': 'List with toggles and selections'
            },
            'account_section': {
                'elements': ['Change password', 'Two-factor auth', 'Delete account'],
                'layout': 'List with navigation arrows'
            },
            'support_section': {
                'elements': ['Help & FAQ', 'Contact us', 'Report issue'],
                'layout': 'List with external links'
            }
        }
    
    def _generate_navigation_structure(self, core_features: List) -> Dict[str, Any]:
        return {
            'primary_navigation': {
                'type': 'Bottom tab bar',
                'items': ['Home', 'Features', 'Activity', 'Profile'],
                'active_states': 'Icon and text color change'
            },
            'secondary_navigation': {
                'type': 'Hamburger menu',
                'items': ['Settings', 'Help', 'About', 'Logout'],
                'behavior': 'Slide out from left'
            },
            'contextual_navigation': {
                'type': 'Header actions',
                'items': ['Search', 'Filter', 'More options'],
                'behavior': 'Context-dependent buttons'
            }
        }
    
    def _generate_design_system(self, app_category: str, target_users: str) -> Dict[str, Any]:
        color_themes = {
            'productivity': {
                'primary': '#2563EB',
                'secondary': '#10B981',
                'accent': '#F59E0B',
                'neutral': '#6B7280'
            },
            'social': {
                'primary': '#8B5CF6',
                'secondary': '#EC4899',
                'accent': '#06B6D4',
                'neutral': '#6B7280'
            },
            'utility': {
                'primary': '#0F172A',
                'secondary': '#475569',
                'accent': '#0EA5E9',
                'neutral': '#94A3B8'
            }
        }
        
        return {
            'colors': color_themes.get(app_category, color_themes['utility']),
            'typography': {
                'heading_font': 'Inter',
                'body_font': 'Inter',
                'font_scale': '1.2 ratio'
            },
            'spacing': {
                'base_unit': '8px',
                'scale': [4, 8, 16, 24, 32, 48, 64]
            },
            'border_radius': {
                'small': '4px',
                'medium': '8px',
                'large': '12px'
            }
        }
    
    def _generate_user_flow(self, core_features: List) -> Dict[str, List[str]]:
        return {
            'new_user_flow': [
                'Landing page',
                'Sign up',
                'Onboarding',
                'Dashboard',
                'First feature use'
            ],
            'returning_user_flow': [
                'Login',
                'Dashboard',
                'Feature access',
                'Action completion'
            ],
            'core_feature_flow': [
                'Feature discovery',
                'Feature activation',
                'Feature use',
                'Result/feedback',
                'Next action suggestion'
            ]
        }
    
    def _generate_responsive_guidelines(self) -> Dict[str, Any]:
        return {
            'breakpoints': {
                'mobile': '320px - 768px',
                'tablet': '768px - 1024px',
                'desktop': '1024px+'
            },
            'layout_principles': [
                'Mobile-first design approach',
                'Flexible grid system',
                'Scalable typography',
                'Touch-friendly interactive elements'
            ],
            'component_adaptations': {
                'mobile': 'Single column layout, bottom navigation',
                'tablet': 'Two column layout, side navigation option',
                'desktop': 'Multi-column layout, top navigation'
            }
        }
    
    def _create_user_journeys(self, app_features: List[Dict]) -> Dict[str, List[str]]:
        return {
            'discovery_journey': [
                'User identifies need',
                'Searches for solution',
                'Finds app',
                'Reviews features',
                'Downloads/signs up'
            ],
            'onboarding_journey': [
                'Welcome and introduction',
                'Account creation',
                'Feature walkthrough',
                'Initial setup',
                'First use'
            ],
            'daily_use_journey': [
                'App launch',
                'Dashboard review',
                'Feature interaction',
                'Task completion',
                'Progress review'
            ]
        }
    
    def _define_interaction_patterns(self, app_features: List[Dict]) -> Dict[str, Any]:
        return {
            'navigation_patterns': {
                'tab_navigation': 'For primary features',
                'modal_presentation': 'For focused tasks',
                'drill_down': 'For hierarchical content'
            },
            'input_patterns': {
                'forms': 'Progressive disclosure',
                'search': 'Instant results with filters',
                'selection': 'Clear visual feedback'
            },
            'feedback_patterns': {
                'success': 'Green checkmark with message',
                'error': 'Red warning with correction guidance',
                'loading': 'Progress indicators with estimated time'
            }
        }
    
    def _generate_accessibility_guidelines(self) -> List[str]:
        return [
            "Minimum 4.5:1 color contrast ratio for text",
            "Touch targets minimum 44x44 pixels",
            "Clear focus indicators for keyboard navigation",
            "Alt text for all images and icons",
            "Semantic markup for screen readers",
            "Error messages clearly associated with form fields",
            "Multiple ways to access the same information",
            "Time limits can be extended or disabled"
        ]
    
    def _define_usability_principles(self) -> List[str]:
        return [
            "Consistency in design patterns and interactions",
            "Clear visual hierarchy and information architecture",
            "Immediate feedback for user actions",
            "Error prevention and recovery assistance",
            "Efficient task completion paths",
            "Customizable user experience when appropriate",
            "Progressive disclosure of complex features",
            "Context-aware help and guidance"
        ]
    
    def _generate_color_schemes(self, app_category: str, brand_preferences: Dict) -> List[Dict[str, Any]]:
        base_schemes = [
            {
                'name': 'Modern Blue',
                'primary': '#2563EB',
                'secondary': '#10B981',
                'accent': '#F59E0B',
                'background': '#F8FAFC',
                'text': '#1E293B'
            },
            {
                'name': 'Warm Purple',
                'primary': '#8B5CF6',
                'secondary': '#EC4899',
                'accent': '#06B6D4',
                'background': '#FEFBFF',
                'text': '#2D1B69'
            },
            {
                'name': 'Professional Gray',
                'primary': '#374151',
                'secondary': '#6B7280',
                'accent': '#0EA5E9',
                'background': '#F9FAFB',
                'text': '#111827'
            }
        ]
        
        return base_schemes
    
    def _generate_typography_system(self, target_market: str) -> Dict[str, Any]:
        return {
            'font_families': {
                'primary': 'Inter, system-ui, sans-serif',
                'secondary': 'JetBrains Mono, monospace',
                'display': 'Outfit, system-ui, sans-serif'
            },
            'font_sizes': {
                'xs': '12px',
                'sm': '14px',
                'base': '16px',
                'lg': '18px',
                'xl': '20px',
                '2xl': '24px',
                '3xl': '30px',
                '4xl': '36px'
            },
            'font_weights': {
                'light': 300,
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            },
            'line_heights': {
                'tight': 1.25,
                'normal': 1.5,
                'relaxed': 1.75
            }
        }
    
    def _generate_iconography_guidelines(self, app_category: str) -> Dict[str, Any]:
        return {
            'style': 'Outlined with 2px stroke width',
            'size_system': ['16px', '20px', '24px', '32px', '48px'],
            'categories': {
                'navigation': 'Home, Settings, Profile, Search',
                'actions': 'Add, Edit, Delete, Save, Share',
                'status': 'Success, Warning, Error, Info',
                'content': 'Text, Image, Video, Document'
            },
            'usage_rules': [
                'Consistent stroke width across all icons',
                'Rounded end caps for strokes',
                'Optical alignment over mathematical alignment',
                'Single color for outlined icons'
            ]
        }
    
    def _generate_layout_principles(self) -> List[str]:
        return [
            "Use consistent grid system (8px base unit)",
            "Maintain clear visual hierarchy with spacing",
            "Group related elements together",
            "Use whitespace effectively to reduce cognitive load",
            "Align elements to create visual order",
            "Scale proportionally across different screen sizes",
            "Prioritize content over decoration",
            "Design for thumb-friendly mobile interactions"
        ]
    
    def _generate_brand_guidelines(self, app_idea: Dict, brand_preferences: Dict) -> Dict[str, Any]:
        return {
            'brand_personality': [
                'Trustworthy and reliable',
                'Modern and innovative',
                'User-friendly and approachable',
                'Professional yet personal'
            ],
            'tone_of_voice': {
                'characteristics': ['Clear', 'Helpful', 'Encouraging', 'Respectful'],
                'avoid': ['Jargon', 'Condescending tone', 'Overly casual', 'Technical complexity']
            },
            'visual_style': {
                'aesthetic': 'Clean, minimal, and purposeful',
                'imagery': 'Real people, diverse representation, authentic situations',
                'illustrations': 'Simple, friendly, consistent style'
            }
        }
    
    def _generate_basic_components(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'Button', 'variants': ['Primary', 'Secondary', 'Text'], 'states': ['Default', 'Hover', 'Active', 'Disabled']},
            {'name': 'Card', 'variants': ['Default', 'Elevated', 'Outlined'], 'content': ['Header', 'Body', 'Actions']},
            {'name': 'Avatar', 'variants': ['Small', 'Medium', 'Large'], 'types': ['Image', 'Initials', 'Icon']},
            {'name': 'Badge', 'variants': ['Primary', 'Secondary', 'Success', 'Warning', 'Error'], 'sizes': ['Small', 'Medium']},
            {'name': 'Divider', 'variants': ['Horizontal', 'Vertical'], 'styles': ['Solid', 'Dashed']}
        ]
    
    def _generate_form_components(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'Input Field', 'types': ['Text', 'Email', 'Password', 'Number'], 'states': ['Default', 'Focus', 'Error', 'Disabled']},
            {'name': 'Textarea', 'variants': ['Resizable', 'Fixed'], 'features': ['Character count', 'Auto-resize']},
            {'name': 'Select Dropdown', 'types': ['Single', 'Multi-select'], 'features': ['Search', 'Clear all']},
            {'name': 'Checkbox', 'variants': ['Default', 'Indeterminate'], 'states': ['Unchecked', 'Checked', 'Disabled']},
            {'name': 'Radio Button', 'grouping': 'Radio group', 'states': ['Unselected', 'Selected', 'Disabled']},
            {'name': 'Toggle Switch', 'variants': ['Default', 'Small'], 'states': ['Off', 'On', 'Disabled']}
        ]
    
    def _generate_navigation_components(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'Navigation Bar', 'types': ['Top nav', 'Bottom nav'], 'features': ['Logo', 'Menu items', 'User actions']},
            {'name': 'Breadcrumb', 'separator': 'Arrow or slash', 'behavior': 'Clickable links to parent pages'},
            {'name': 'Tabs', 'variants': ['Horizontal', 'Vertical'], 'states': ['Active', 'Inactive', 'Disabled']},
            {'name': 'Pagination', 'types': ['Numbers', 'Previous/Next'], 'features': ['Page size selector', 'Jump to page']},
            {'name': 'Menu', 'types': ['Dropdown', 'Context menu'], 'features': ['Icons', 'Keyboard shortcuts', 'Dividers']}
        ]
    
    def _generate_data_display_components(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'Table', 'features': ['Sorting', 'Filtering', 'Row selection'], 'responsive': 'Horizontal scroll on mobile'},
            {'name': 'List', 'variants': ['Simple', 'With avatars', 'With actions'], 'features': ['Dividers', 'Zebra striping']},
            {'name': 'Progress Bar', 'types': ['Linear', 'Circular'], 'variants': ['Determinate', 'Indeterminate']},
            {'name': 'Chart', 'types': ['Line', 'Bar', 'Pie', 'Area'], 'features': ['Tooltips', 'Legend', 'Zoom']},
            {'name': 'Timeline', 'variants': ['Vertical', 'Horizontal'], 'features': ['Icons', 'Dates', 'Descriptions']}
        ]
    
    def _generate_feedback_components(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'Alert', 'types': ['Success', 'Warning', 'Error', 'Info'], 'features': ['Dismissible', 'Actions']},
            {'name': 'Toast', 'position': ['Top', 'Bottom'], 'duration': 'Auto-dismiss or persistent'},
            {'name': 'Modal', 'sizes': ['Small', 'Medium', 'Large', 'Fullscreen'], 'features': ['Header', 'Body', 'Footer']},
            {'name': 'Tooltip', 'triggers': ['Hover', 'Click'], 'positions': ['Top', 'Bottom', 'Left', 'Right']},
            {'name': 'Loading Spinner', 'variants': ['Small', 'Medium', 'Large'], 'types': ['Circular', 'Linear']}
        ]
    
    def _generate_component_usage_guidelines(self) -> Dict[str, str]:
        return {
            'buttons': 'Use primary buttons for main actions, secondary for supporting actions',
            'cards': 'Group related content and provide clear visual boundaries',
            'forms': 'Provide clear labels, validation feedback, and logical tab order',
            'navigation': 'Keep navigation consistent and provide clear current location',
            'feedback': 'Provide immediate feedback for user actions and system status'
        }
    
    def _generate_component_code_examples(self) -> Dict[str, str]:
        return {
            'button': '''
            <button class="btn btn-primary">
                Primary Button
            </button>
            ''',
            'card': '''
            <div class="card">
                <div class="card-header">Title</div>
                <div class="card-body">Content</div>
                <div class="card-footer">Actions</div>
            </div>
            ''',
            'input': '''
            <div class="input-group">
                <label for="email">Email</label>
                <input type="email" id="email" class="form-input" />
            </div>
            '''
        }
    
    def _create_prototype_structure(self, wireframes: Dict) -> Dict[str, Any]:
        return {
            'screen_hierarchy': list(wireframes.keys()),
            'navigation_flow': 'Defined by wireframe connections',
            'interaction_zones': 'Clickable areas defined in wireframes',
            'content_areas': 'Text, image, and media placeholders'
        }
    
    def _define_interaction_specifications(self, wireframes: Dict) -> List[Dict[str, Any]]:
        return [
            {'interaction': 'Tap', 'response': 'Visual feedback + navigation or action'},
            {'interaction': 'Swipe', 'response': 'Content scrolling or screen transition'},
            {'interaction': 'Pinch', 'response': 'Zoom in/out for image content'},
            {'interaction': 'Long press', 'response': 'Context menu or additional options'}
        ]
    
    def _generate_animation_guidelines(self) -> Dict[str, Any]:
        return {
            'duration': {
                'micro': '100-200ms for hover states',
                'short': '200-500ms for transitions',
                'medium': '500-1000ms for complex animations'
            },
            'easing': {
                'ease_out': 'For elements entering the screen',
                'ease_in': 'For elements leaving the screen',
                'ease_in_out': 'For elements moving within screen'
            },
            'principles': [
                'Animations should feel natural and purposeful',
                'Respect user preferences for reduced motion',
                'Use consistent timing across similar interactions',
                'Avoid excessive or distracting animations'
            ]
        }
    
    def _define_responsive_breakpoints(self) -> Dict[str, str]:
        return {
            'xs': '320px',
            'sm': '640px',
            'md': '768px',
            'lg': '1024px',
            'xl': '1280px',
            '2xl': '1536px'
        }
    
    def _generate_design_testing_checklist(self) -> List[str]:
        return [
            "Test across different screen sizes and orientations",
            "Verify color contrast meets accessibility standards",
            "Check touch target sizes on mobile devices",
            "Test keyboard navigation flow",
            "Validate form error states and messaging",
            "Review loading states and empty states",
            "Test with different content lengths",
            "Verify consistency across all screens",
            "Check performance impact of animations",
            "Test with assistive technologies"
        ]

design_generator = DesignGenerator()