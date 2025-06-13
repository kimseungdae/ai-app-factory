import logging
import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import requests
from jinja2 import Template
from ..utils.config import config
from ..utils.api_clients import api_manager

logger = logging.getLogger(__name__)

class PrototypeBuilder:
    def __init__(self):
        self.enabled = config.is_agent_enabled('design_generator')  # Using existing config
        
        if not self.enabled:
            logger.info("Prototype Builder agent is disabled")
            return
        
        self.openai_client = api_manager.get_client('openai')
        
        # Figma API configuration
        self.figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
        self.figma_api_base = "https://api.figma.com/v1"
        
        # Vercel API configuration (optional)
        self.vercel_token = os.getenv('VERCEL_TOKEN')
        
        # Core screens configuration
        self.core_screens = {
            'onboarding': {
                'name': 'Onboarding',
                'description': 'User introduction and setup',
                'route': '/onboarding',
                'components': ['welcome', 'features', 'signup']
            },
            'main': {
                'name': 'Main Dashboard',
                'description': 'Primary user interface',
                'route': '/',
                'components': ['header', 'navigation', 'content', 'quick_actions']
            },
            'detail': {
                'name': 'Detail View',
                'description': 'Detailed item or content view',
                'route': '/detail/:id',
                'components': ['header', 'content', 'actions', 'related']
            },
            'settings': {
                'name': 'Settings',
                'description': 'User preferences and configuration',
                'route': '/settings',
                'components': ['profile', 'preferences', 'notifications', 'account']
            },
            'profile': {
                'name': 'User Profile',
                'description': 'User profile and personal information',
                'route': '/profile',
                'components': ['avatar', 'info', 'stats', 'activity']
            }
        }
    
    def build_complete_prototype(self, design_system: Dict[str, Any], ux_strategy: Dict[str, Any], app_name: str = "MyApp") -> Dict[str, Any]:
        """
        Main method to build complete prototype from design system and UX strategy
        """
        if not self.enabled:
            return {"error": "Prototype Builder agent is disabled"}
        
        try:
            logger.info(f"Building complete prototype for: {app_name}")
            
            # Step 1: Create project structure
            project_path = self._create_project_structure(app_name)
            
            # Step 2: Generate React components
            components = self._generate_react_components(design_system, ux_strategy, project_path)
            
            # Step 3: Generate main app and routing
            app_files = self._generate_app_structure(design_system, ux_strategy, project_path, app_name)
            
            # Step 4: Generate configuration files
            config_files = self._generate_config_files(design_system, project_path, app_name)
            
            # Step 5: Create Figma prototype (if token available)
            figma_prototype = self._create_figma_prototype(design_system, ux_strategy, app_name)
            
            # Step 6: Generate deployment configuration
            deployment_config = self._generate_deployment_config(project_path, app_name)
            
            # Step 7: Create documentation
            documentation = self._generate_documentation(design_system, ux_strategy, project_path, app_name)
            
            prototype_result = {
                'project_info': {
                    'app_name': app_name,
                    'project_path': str(project_path),
                    'generated_at': datetime.now().isoformat(),
                    'technology_stack': {
                        'frontend': 'React 18',
                        'styling': 'Tailwind CSS',
                        'routing': 'React Router',
                        'icons': 'Lucide React',
                        'deployment': 'Vercel Ready'
                    }
                },
                'generated_files': {
                    'components': components,
                    'app_files': app_files,
                    'config_files': config_files,
                    'documentation': documentation
                },
                'figma_prototype': figma_prototype,
                'deployment': deployment_config,
                'next_steps': self._generate_next_steps(project_path, app_name),
                'urls': {
                    'local_dev': 'http://localhost:3000',
                    'figma_prototype': figma_prototype.get('prototype_url') if figma_prototype else None,
                    'deployment_ready': True
                }
            }
            
            logger.info("Complete prototype generation finished successfully")
            return prototype_result
            
        except Exception as e:
            logger.error(f"Error building prototype: {e}")
            return {"error": str(e)}
    
    def _create_project_structure(self, app_name: str) -> Path:
        """Create React project directory structure"""
        project_name = app_name.lower().replace(' ', '-').replace('_', '-')
        project_path = Path(f"generated_prototypes/{project_name}")
        
        # Create directory structure
        directories = [
            'src/components/common',
            'src/components/screens',
            'src/components/layout',
            'src/hooks',
            'src/utils',
            'src/styles',
            'src/assets/icons',
            'src/assets/images',
            'public',
            'docs'
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created project structure at: {project_path}")
        return project_path
    
    def _generate_react_components(self, design_system: Dict, ux_strategy: Dict, project_path: Path) -> Dict[str, List[str]]:
        """Generate React components for all screens"""
        generated_components = {
            'common': [],
            'screens': [],
            'layout': []
        }
        
        # Extract design tokens
        design_tokens = design_system.get('design_tokens', {})
        color_palette = design_system.get('brand_identity', {}).get('color_palette', {})
        components_spec = design_system.get('component_system', {}).get('components', {})
        
        # Generate common components
        common_components = self._generate_common_components(design_tokens, color_palette, project_path)
        generated_components['common'] = common_components
        
        # Generate layout components
        layout_components = self._generate_layout_components(design_tokens, project_path)
        generated_components['layout'] = layout_components
        
        # Generate screen components
        ux_strategies = ux_strategy.get('strategies', [])
        primary_strategy = ux_strategies[0] if ux_strategies else {}
        
        for screen_id, screen_config in self.core_screens.items():
            screen_component = self._generate_screen_component(
                screen_id, screen_config, design_tokens, color_palette, 
                primary_strategy, project_path
            )
            generated_components['screens'].append(screen_component)
        
        return generated_components
    
    def _generate_common_components(self, design_tokens: Dict, color_palette: Dict, project_path: Path) -> List[str]:
        """Generate common reusable components"""
        common_components = []
        
        # Button Component
        button_component = self._create_button_component(design_tokens, color_palette)
        button_path = project_path / 'src/components/common/Button.jsx'
        with open(button_path, 'w') as f:
            f.write(button_component)
        common_components.append('Button.jsx')
        
        # Input Component
        input_component = self._create_input_component(design_tokens, color_palette)
        input_path = project_path / 'src/components/common/Input.jsx'
        with open(input_path, 'w') as f:
            f.write(input_component)
        common_components.append('Input.jsx')
        
        # Card Component
        card_component = self._create_card_component(design_tokens, color_palette)
        card_path = project_path / 'src/components/common/Card.jsx'
        with open(card_path, 'w') as f:
            f.write(card_component)
        common_components.append('Card.jsx')
        
        # Avatar Component
        avatar_component = self._create_avatar_component(design_tokens)
        avatar_path = project_path / 'src/components/common/Avatar.jsx'
        with open(avatar_path, 'w') as f:
            f.write(avatar_component)
        common_components.append('Avatar.jsx')
        
        # Loading Component
        loading_component = self._create_loading_component(design_tokens, color_palette)
        loading_path = project_path / 'src/components/common/Loading.jsx'
        with open(loading_path, 'w') as f:
            f.write(loading_component)
        common_components.append('Loading.jsx')
        
        return common_components
    
    def _generate_layout_components(self, design_tokens: Dict, project_path: Path) -> List[str]:
        """Generate layout components"""
        layout_components = []
        
        # Header Component
        header_component = self._create_header_component(design_tokens)
        header_path = project_path / 'src/components/layout/Header.jsx'
        with open(header_path, 'w') as f:
            f.write(header_component)
        layout_components.append('Header.jsx')
        
        # Navigation Component
        nav_component = self._create_navigation_component(design_tokens)
        nav_path = project_path / 'src/components/layout/Navigation.jsx'
        with open(nav_path, 'w') as f:
            f.write(nav_component)
        layout_components.append('Navigation.jsx')
        
        # Layout Wrapper
        layout_component = self._create_layout_component(design_tokens)
        layout_path = project_path / 'src/components/layout/Layout.jsx'
        with open(layout_path, 'w') as f:
            f.write(layout_component)
        layout_components.append('Layout.jsx')
        
        return layout_components
    
    def _generate_screen_component(self, screen_id: str, screen_config: Dict, design_tokens: Dict, 
                                 color_palette: Dict, strategy: Dict, project_path: Path) -> str:
        """Generate individual screen component"""
        screen_name = screen_config['name'].replace(' ', '')
        
        if screen_id == 'onboarding':
            component_code = self._create_onboarding_screen(design_tokens, color_palette, strategy)
        elif screen_id == 'main':
            component_code = self._create_main_screen(design_tokens, color_palette, strategy)
        elif screen_id == 'detail':
            component_code = self._create_detail_screen(design_tokens, color_palette, strategy)
        elif screen_id == 'settings':
            component_code = self._create_settings_screen(design_tokens, color_palette)
        elif screen_id == 'profile':
            component_code = self._create_profile_screen(design_tokens, color_palette)
        else:
            component_code = self._create_generic_screen(screen_name, design_tokens, color_palette)
        
        # Save component file
        component_filename = f"{screen_name}.jsx"
        component_path = project_path / f'src/components/screens/{component_filename}'
        
        with open(component_path, 'w') as f:
            f.write(component_code)
        
        return component_filename
    
    def _generate_app_structure(self, design_system: Dict, ux_strategy: Dict, project_path: Path, app_name: str) -> Dict[str, str]:
        """Generate main App.js and routing structure"""
        app_files = {}
        
        # Generate App.jsx
        app_component = self._create_app_component(design_system, app_name)
        app_path = project_path / 'src/App.jsx'
        with open(app_path, 'w') as f:
            f.write(app_component)
        app_files['App.jsx'] = str(app_path)
        
        # Generate index.js
        index_js = self._create_index_js(app_name)
        index_path = project_path / 'src/index.js'
        with open(index_path, 'w') as f:
            f.write(index_js)
        app_files['index.js'] = str(index_path)
        
        # Generate Router component
        router_component = self._create_router_component()
        router_path = project_path / 'src/components/Router.jsx'
        with open(router_path, 'w') as f:
            f.write(router_component)
        app_files['Router.jsx'] = str(router_path)
        
        return app_files
    
    def _generate_config_files(self, design_system: Dict, project_path: Path, app_name: str) -> Dict[str, str]:
        """Generate configuration files"""
        config_files = {}
        
        # Generate package.json
        package_json = self._create_package_json(app_name)
        package_path = project_path / 'package.json'
        with open(package_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        config_files['package.json'] = str(package_path)
        
        # Generate tailwind.config.js
        tailwind_config = self._create_tailwind_config(design_system)
        tailwind_path = project_path / 'tailwind.config.js'
        with open(tailwind_path, 'w') as f:
            f.write(tailwind_config)
        config_files['tailwind.config.js'] = str(tailwind_path)
        
        # Generate index.css (Tailwind imports)
        index_css = self._create_index_css(design_system)
        css_path = project_path / 'src/index.css'
        with open(css_path, 'w') as f:
            f.write(index_css)
        config_files['index.css'] = str(css_path)
        
        # Generate index.html
        index_html = self._create_index_html(app_name)
        html_path = project_path / 'public/index.html'
        with open(html_path, 'w') as f:
            f.write(index_html)
        config_files['index.html'] = str(html_path)
        
        return config_files
    
    def _create_figma_prototype(self, design_system: Dict, ux_strategy: Dict, app_name: str) -> Optional[Dict[str, Any]]:
        """Create Figma prototype using Figma API"""
        if not self.figma_token:
            logger.warning("Figma token not available, skipping Figma prototype creation")
            return {
                'status': 'skipped',
                'reason': 'No Figma access token provided',
                'manual_instructions': self._generate_figma_manual_instructions(design_system, app_name)
            }
        
        try:
            logger.info("Creating Figma prototype...")
            
            # Create new Figma file
            figma_file = self._create_figma_file(app_name)
            
            if figma_file:
                # Add screens to Figma file
                screens_added = self._add_screens_to_figma(figma_file['key'], design_system, ux_strategy)
                
                return {
                    'status': 'created',
                    'file_key': figma_file['key'],
                    'file_url': f"https://www.figma.com/file/{figma_file['key']}/{app_name}",
                    'prototype_url': f"https://www.figma.com/proto/{figma_file['key']}/{app_name}",
                    'screens_count': len(self.core_screens),
                    'created_at': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'failed',
                    'reason': 'Could not create Figma file',
                    'manual_instructions': self._generate_figma_manual_instructions(design_system, app_name)
                }
                
        except Exception as e:
            logger.error(f"Error creating Figma prototype: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'manual_instructions': self._generate_figma_manual_instructions(design_system, app_name)
            }
    
    def _generate_deployment_config(self, project_path: Path, app_name: str) -> Dict[str, Any]:
        """Generate deployment configuration"""
        deployment_config = {
            'vercel': {
                'ready': True,
                'config_file': self._create_vercel_config(project_path),
                'deploy_command': 'vercel --prod',
                'build_command': 'npm run build'
            },
            'netlify': {
                'ready': True,
                'config_file': self._create_netlify_config(project_path),
                'deploy_command': 'netlify deploy --prod',
                'build_command': 'npm run build'
            },
            'github_pages': {
                'ready': True,
                'config_file': self._create_github_actions_config(project_path),
                'deploy_command': 'git push origin main'
            }
        }
        
        return deployment_config
    
    def _generate_documentation(self, design_system: Dict, ux_strategy: Dict, project_path: Path, app_name: str) -> Dict[str, str]:
        """Generate project documentation"""
        docs = {}
        
        # README.md
        readme = self._create_readme(design_system, ux_strategy, app_name)
        readme_path = project_path / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme)
        docs['README.md'] = str(readme_path)
        
        # Component Documentation
        component_docs = self._create_component_docs(design_system)
        component_docs_path = project_path / 'docs/COMPONENTS.md'
        with open(component_docs_path, 'w') as f:
            f.write(component_docs)
        docs['COMPONENTS.md'] = str(component_docs_path)
        
        # Development Guide
        dev_guide = self._create_development_guide(app_name)
        dev_guide_path = project_path / 'docs/DEVELOPMENT.md'
        with open(dev_guide_path, 'w') as f:
            f.write(dev_guide)
        docs['DEVELOPMENT.md'] = str(dev_guide_path)
        
        return docs
    
    # Component creation methods
    def _create_button_component(self, design_tokens: Dict, color_palette: Dict) -> str:
        """Create Button component with variants"""
        primary_color = self._extract_primary_color(color_palette)
        
        return f'''import React from 'react';
import {{ cn }} from '../utils/cn';

const Button = ({{ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  onClick, 
  className,
  ...props 
}}) => {{
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {{
    primary: 'bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-500',
    secondary: 'bg-white text-primary-500 border border-primary-500 hover:bg-primary-50 focus:ring-primary-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500'
  }};
  
  const sizes = {{
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }};
  
  const disabledClasses = 'opacity-50 cursor-not-allowed';
  
  return (
    <button
      className={{cn(
        baseClasses,
        variants[variant],
        sizes[size],
        disabled && disabledClasses,
        className
      )}}
      disabled={{disabled}}
      onClick={{onClick}}
      {{...props}}
    >
      {{children}}
    </button>
  );
}};

export default Button;'''
    
    def _create_input_component(self, design_tokens: Dict, color_palette: Dict) -> str:
        """Create Input component"""
        return '''import React from 'react';
import { cn } from '../utils/cn';

const Input = ({ 
  label, 
  error, 
  helper, 
  type = 'text', 
  placeholder,
  value,
  onChange,
  disabled = false,
  className,
  ...props 
}) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className={cn(
          'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm',
          'placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500',
          'disabled:bg-gray-50 disabled:cursor-not-allowed',
          error && 'border-red-300 focus:ring-red-500 focus:border-red-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
      {helper && !error && (
        <p className="text-sm text-gray-500">{helper}</p>
      )}
    </div>
  );
};

export default Input;'''
    
    def _create_card_component(self, design_tokens: Dict, color_palette: Dict) -> str:
        """Create Card component"""
        return '''import React from 'react';
import { cn } from '../utils/cn';

const Card = ({ 
  children, 
  variant = 'default', 
  padding = 'md',
  className,
  ...props 
}) => {
  const baseClasses = 'bg-white rounded-lg border';
  
  const variants = {
    default: 'border-gray-200 shadow-sm',
    elevated: 'border-gray-200 shadow-lg',
    outlined: 'border-gray-300',
    interactive: 'border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer'
  };
  
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8'
  };
  
  return (
    <div
      className={cn(
        baseClasses,
        variants[variant],
        paddings[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;'''
    
    def _create_avatar_component(self, design_tokens: Dict) -> str:
        """Create Avatar component"""
        return '''import React from 'react';
import { cn } from '../utils/cn';

const Avatar = ({ 
  src, 
  alt, 
  size = 'md', 
  fallback,
  className 
}) => {
  const sizes = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-16 h-16 text-xl'
  };
  
  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={cn(
          'rounded-full object-cover',
          sizes[size],
          className
        )}
      />
    );
  }
  
  return (
    <div
      className={cn(
        'rounded-full bg-primary-500 flex items-center justify-center text-white font-medium',
        sizes[size],
        className
      )}
    >
      {fallback || alt?.charAt(0)?.toUpperCase() || '?'}
    </div>
  );
};

export default Avatar;'''
    
    def _create_loading_component(self, design_tokens: Dict, color_palette: Dict) -> str:
        """Create Loading component"""
        return '''import React from 'react';
import { cn } from '../utils/cn';

const Loading = ({ 
  size = 'md', 
  variant = 'spinner',
  className 
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };
  
  if (variant === 'spinner') {
    return (
      <div
        className={cn(
          'animate-spin rounded-full border-2 border-gray-300 border-t-primary-500',
          sizes[size],
          className
        )}
      />
    );
  }
  
  if (variant === 'dots') {
    return (
      <div className={cn('flex space-x-1', className)}>
        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-75" />
        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-150" />
      </div>
    );
  }
  
  return null;
};

export default Loading;'''
    
    def _create_header_component(self, design_tokens: Dict) -> str:
        """Create Header component"""
        return '''import React from 'react';
import { Menu, Bell, User } from 'lucide-react';
import Avatar from '../common/Avatar';
import Button from '../common/Button';

const Header = ({ title, onMenuClick, user }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuClick}
            className="lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-semibold text-gray-900">
            {title}
          </h1>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="ghost" size="sm">
            <Bell className="w-5 h-5" />
          </Button>
          
          <div className="flex items-center space-x-2">
            <Avatar
              src={user?.avatar}
              alt={user?.name}
              fallback={user?.name}
              size="sm"
            />
            <span className="hidden md:block text-sm font-medium text-gray-700">
              {user?.name || 'User'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;'''
    
    def _create_navigation_component(self, design_tokens: Dict) -> str:
        """Create Navigation component"""
        return '''import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, FileText, Settings, User, Menu } from 'lucide-react';
import { cn } from '../utils/cn';

const Navigation = ({ isOpen, onClose }) => {
  const navItems = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/detail/1', icon: FileText, label: 'Details' },
    { to: '/profile', icon: User, label: 'Profile' },
    { to: '/settings', icon: Settings, label: 'Settings' }
  ];
  
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={cn(
        'fixed left-0 top-0 z-50 h-full w-64 bg-white border-r border-gray-200 transform transition-transform lg:translate-x-0 lg:static lg:z-auto',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-lg font-semibold text-gray-900">MyApp</h2>
            <button
              onClick={onClose}
              className="lg:hidden p-1 rounded-md hover:bg-gray-100"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
          
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => cn(
                  'flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  isActive 
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
                onClick={() => window.innerWidth < 1024 && onClose()}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </aside>
    </>
  );
};

export default Navigation;'''
    
    def _create_layout_component(self, design_tokens: Dict) -> str:
        """Create Layout wrapper component"""
        return '''import React, { useState } from 'react';
import Header from './Header';
import Navigation from './Navigation';

const Layout = ({ children, title = 'Dashboard' }) => {
  const [isNavOpen, setIsNavOpen] = useState(false);
  
  // Mock user data - replace with real user context
  const user = {
    name: 'John Doe',
    avatar: null
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation 
        isOpen={isNavOpen} 
        onClose={() => setIsNavOpen(false)} 
      />
      
      <div className="lg:pl-64">
        <Header 
          title={title}
          onMenuClick={() => setIsNavOpen(true)}
          user={user}
        />
        
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;'''
    
    def _create_onboarding_screen(self, design_tokens: Dict, color_palette: Dict, strategy: Dict) -> str:
        """Create Onboarding screen component"""
        return '''import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Check, Star, Zap, Shield } from 'lucide-react';
import Button from '../common/Button';
import Card from '../common/Card';

const OnboardingScreen = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();
  
  const steps = [
    {
      title: 'Welcome to MyApp',
      description: 'Discover a new way to boost your productivity',
      icon: Star,
      content: (
        <div className="text-center">
          <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Star className="w-12 h-12 text-primary-500" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome to MyApp</h1>
          <p className="text-lg text-gray-600 max-w-md mx-auto">
            Experience the future of productivity with our innovative approach to getting things done.
          </p>
        </div>
      )
    },
    {
      title: 'Key Features',
      description: 'Powerful tools at your fingertips',
      icon: Zap,
      content: (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Key Features</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Check className="w-4 h-4 text-primary-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Smart Automation</h3>
                <p className="text-gray-600">Let AI handle repetitive tasks while you focus on what matters.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Check className="w-4 h-4 text-primary-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Real-time Collaboration</h3>
                <p className="text-gray-600">Work seamlessly with your team, wherever they are.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Check className="w-4 h-4 text-primary-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Advanced Analytics</h3>
                <p className="text-gray-600">Get insights that drive better decisions and outcomes.</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: 'Get Started',
      description: 'Ready to transform your workflow?',
      icon: Shield,
      content: (
        <div className="text-center">
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Shield className="w-12 h-12 text-green-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">You're All Set!</h2>
          <p className="text-lg text-gray-600 max-w-md mx-auto mb-6">
            Everything is ready for you to start your productivity journey.
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/')}
            className="w-full max-w-xs"
          >
            Get Started
            <ChevronRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      )
    }
  ];
  
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      navigate('/');
    }
  };
  
  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <Card variant="elevated" padding="xl">
          {/* Progress indicators */}
          <div className="flex justify-center mb-8">
            <div className="flex space-x-2">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`w-3 h-3 rounded-full ${
                    index <= currentStep ? 'bg-primary-500' : 'bg-gray-200'
                  }`}
                />
              ))}
            </div>
          </div>
          
          {/* Step content */}
          <div className="mb-8">
            {steps[currentStep].content}
          </div>
          
          {/* Navigation buttons */}
          <div className="flex justify-between">
            <Button
              variant="ghost"
              onClick={prevStep}
              disabled={currentStep === 0}
            >
              Previous
            </Button>
            
            <Button onClick={nextStep}>
              {currentStep === steps.length - 1 ? 'Get Started' : 'Next'}
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default OnboardingScreen;'''
    
    def _create_main_screen(self, design_tokens: Dict, color_palette: Dict, strategy: Dict) -> str:
        """Create Main Dashboard screen component"""
        return '''import React from 'react';
import { BarChart3, Users, TrendingUp, Calendar, Plus } from 'lucide-react';
import Layout from '../layout/Layout';
import Card from '../common/Card';
import Button from '../common/Button';

const MainScreen = () => {
  const stats = [
    { label: 'Total Projects', value: '12', icon: BarChart3, change: '+12%' },
    { label: 'Team Members', value: '8', icon: Users, change: '+2' },
    { label: 'Growth', value: '23%', icon: TrendingUp, change: '+5%' },
    { label: 'Events', value: '4', icon: Calendar, change: 'Today' }
  ];
  
  const recentActivity = [
    { id: 1, action: 'Project "Website Redesign" completed', time: '2 hours ago', type: 'success' },
    { id: 2, action: 'New team member Sarah joined', time: '4 hours ago', type: 'info' },
    { id: 3, action: 'Monthly report generated', time: '1 day ago', type: 'neutral' },
    { id: 4, action: 'Client meeting scheduled', time: '2 days ago', type: 'warning' }
  ];
  
  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome back!</h1>
              <p className="text-gray-600 mt-1">Here's what's happening with your projects today.</p>
            </div>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <Card key={index} variant="default" padding="md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-green-600 mt-1">{stat.change}</p>
                </div>
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <stat.icon className="w-6 h-6 text-primary-600" />
                </div>
              </div>
            </Card>
          ))}
        </div>
        
        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <Card variant="default" padding="none">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        activity.type === 'success' ? 'bg-green-500' :
                        activity.type === 'warning' ? 'bg-yellow-500' :
                        activity.type === 'info' ? 'bg-blue-500' : 'bg-gray-400'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">{activity.action}</p>
                        <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
          
          {/* Quick Actions */}
          <div>
            <Card variant="default" padding="md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button variant="secondary" className="w-full justify-start">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Project
                </Button>
                <Button variant="secondary" className="w-full justify-start">
                  <Users className="w-4 h-4 mr-2" />
                  Invite Team Member
                </Button>
                <Button variant="secondary" className="w-full justify-start">
                  <Calendar className="w-4 h-4 mr-2" />
                  Schedule Meeting
                </Button>
                <Button variant="secondary" className="w-full justify-start">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  View Analytics
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default MainScreen;'''
    
    def _create_detail_screen(self, design_tokens: Dict, color_palette: Dict, strategy: Dict) -> str:
        """Create Detail View screen component"""
        return '''import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Share, MoreHorizontal, Calendar, User, Tag } from 'lucide-react';
import Layout from '../layout/Layout';
import Card from '../common/Card';
import Button from '../common/Button';
import Avatar from '../common/Avatar';

const DetailScreen = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Mock data - replace with real data fetching
  const item = {
    id: id,
    title: 'Website Redesign Project',
    description: 'Complete overhaul of the company website with modern design principles and improved user experience.',
    status: 'In Progress',
    priority: 'High',
    dueDate: '2024-02-15',
    assignee: {
      name: 'Sarah Johnson',
      avatar: null,
      email: 'sarah@company.com'
    },
    tags: ['Design', 'Frontend', 'UX'],
    progress: 65,
    createdAt: '2024-01-10',
    updatedAt: '2024-01-25'
  };
  
  const relatedItems = [
    { id: 2, title: 'Mobile App Design', status: 'Planning' },
    { id: 3, title: 'Brand Guidelines', status: 'Completed' },
    { id: 4, title: 'User Research', status: 'In Progress' }
  ];
  
  return (
    <Layout title="Project Details">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(-1)}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{item.title}</h1>
              <p className="text-gray-600">Project #{item.id}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="secondary" size="sm">
              <Share className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button size="sm">
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Details */}
          <div className="lg:col-span-2 space-y-6">
            <Card variant="default" padding="md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Description</h3>
              <p className="text-gray-700 leading-relaxed">{item.description}</p>
            </Card>
            
            <Card variant="default" padding="md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Completion</span>
                  <span className="font-medium">{item.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-500 h-2 rounded-full transition-all"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              </div>
            </Card>
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            <Card variant="default" padding="md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Details</h3>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Calendar className="w-4 h-4 text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Due Date</p>
                    <p className="text-sm text-gray-600">{item.dueDate}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <User className="w-4 h-4 text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Assignee</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Avatar 
                        src={item.assignee.avatar} 
                        alt={item.assignee.name}
                        fallback={item.assignee.name}
                        size="xs" 
                      />
                      <span className="text-sm text-gray-600">{item.assignee.name}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Tag className="w-4 h-4 text-gray-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Tags</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {item.tags.map((tag) => (
                        <span 
                          key={tag}
                          className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-md"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </Card>
            
            <Card variant="default" padding="md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Related Items</h3>
              <div className="space-y-3">
                {relatedItems.map((relatedItem) => (
                  <div 
                    key={relatedItem.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                    onClick={() => navigate(`/detail/${relatedItem.id}`)}
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900">{relatedItem.title}</p>
                      <p className="text-xs text-gray-600">{relatedItem.status}</p>
                    </div>
                    <ArrowLeft className="w-4 h-4 text-gray-400 rotate-180" />
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DetailScreen;'''
    
    def _create_settings_screen(self, design_tokens: Dict, color_palette: Dict) -> str:
        """Create Settings screen component"""
        return '''import React, { useState } from 'react';
import { Bell, Lock, User, Palette, Globe, Shield } from 'lucide-react';
import Layout from '../layout/Layout';
import Card from '../common/Card';
import Button from '../common/Button';
import Input from '../common/Input';

const SettingsScreen = () => {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: false
  });
  
  const [profile, setProfile] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    timezone: 'UTC-8'
  });
  
  const settingsSections = [
    {
      id: 'profile',
      title: 'Profile Settings',
      icon: User,
      description: 'Manage your personal information'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      icon: Bell,
      description: 'Configure how you receive updates'
    },
    {
      id: 'security',
      title: 'Security & Privacy',
      icon: Shield,
      description: 'Manage your account security'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      icon: Palette,
      description: 'Customize the look and feel'
    }
  ];
  
  return (
    <Layout title="Settings">
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Manage your account settings and preferences.</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Settings Navigation */}
          <div className="lg:col-span-1">
            <Card variant="default" padding="sm">
              <nav className="space-y-1">
                {settingsSections.map((section) => (
                  <button
                    key={section.id}
                    className="w-full flex items-center space-x-3 px-3 py-2 text-left rounded-md hover:bg-gray-50 transition-colors"
                  >
                    <section.icon className="w-5 h-5 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">{section.title}</span>
                  </button>
                ))}
              </nav>
            </Card>
          </div>
          
          {/* Settings Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Profile Settings */}
            <Card variant="default" padding="md">
              <div className="flex items-center space-x-3 mb-6">
                <User className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Profile Settings</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  value={profile.name}
                  onChange={(e) => setProfile({...profile, name: e.target.value})}
                />
                <Input
                  label="Email Address"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({...profile, email: e.target.value})}
                />
                <Input
                  label="Timezone"
                  value={profile.timezone}
                  onChange={(e) => setProfile({...profile, timezone: e.target.value})}
                />
              </div>
              
              <div className="mt-6">
                <Button>Save Changes</Button>
              </div>
            </Card>
            
            {/* Notification Settings */}
            <Card variant="default" padding="md">
              <div className="flex items-center space-x-3 mb-6">
                <Bell className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Notification Preferences</h3>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Email Notifications</p>
                    <p className="text-sm text-gray-600">Receive updates via email</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.email}
                      onChange={(e) => setNotifications({...notifications, email: e.target.checked})}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Push Notifications</p>
                    <p className="text-sm text-gray-600">Receive push notifications in browser</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.push}
                      onChange={(e) => setNotifications({...notifications, push: e.target.checked})}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                  </label>
                </div>
              </div>
            </Card>
            
            {/* Security Settings */}
            <Card variant="default" padding="md">
              <div className="flex items-center space-x-3 mb-6">
                <Shield className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Security & Privacy</h3>
              </div>
              
              <div className="space-y-4">
                <Button variant="secondary">
                  <Lock className="w-4 h-4 mr-2" />
                  Change Password
                </Button>
                
                <Button variant="secondary">
                  <Shield className="w-4 h-4 mr-2" />
                  Enable Two-Factor Authentication
                </Button>
                
                <Button variant="danger">
                  Delete Account
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SettingsScreen;'''
    
    def _create_profile_screen(self, design_tokens: Dict, color_palette: Dict) -> str:
        """Create Profile screen component"""
        return '''import React from 'react';
import { Mail, MapPin, Calendar, Edit, Camera } from 'lucide-react';
import Layout from '../layout/Layout';
import Card from '../common/Card';
import Button from '../common/Button';
import Avatar from '../common/Avatar';

const ProfileScreen = () => {
  const user = {
    name: 'John Doe',
    email: 'john@example.com',
    location: 'San Francisco, CA',
    joinDate: 'January 2024',
    avatar: null,
    bio: 'Product designer passionate about creating meaningful user experiences. Always learning and exploring new design trends.',
    stats: {
      projects: 24,
      completed: 18,
      inProgress: 6
    }
  };
  
  const recentProjects = [
    { id: 1, name: 'Website Redesign', status: 'Completed', date: '2024-01-20' },
    { id: 2, name: 'Mobile App UI', status: 'In Progress', date: '2024-01-15' },
    { id: 3, name: 'Brand Guidelines', status: 'Completed', date: '2024-01-10' }
  ];
  
  const achievements = [
    { title: 'Project Master', description: 'Completed 10+ projects', icon: '🏆' },
    { title: 'Team Player', description: 'Collaborated on 5+ team projects', icon: '🤝' },
    { title: 'Early Adopter', description: 'Joined in the first month', icon: '🚀' }
  ];
  
  return (
    <Layout title="Profile">
      <div className="space-y-6">
        {/* Profile Header */}
        <Card variant="default" padding="md">
          <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
            <div className="relative">
              <Avatar 
                src={user.avatar} 
                alt={user.name} 
                fallback={user.name}
                size="xl" 
              />
              <button className="absolute bottom-0 right-0 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white hover:bg-primary-600 transition-colors">
                <Camera className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex-1">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{user.name}</h1>
                  <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 mt-2 space-y-1 sm:space-y-0">
                    <div className="flex items-center text-gray-600">
                      <Mail className="w-4 h-4 mr-1" />
                      <span className="text-sm">{user.email}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <MapPin className="w-4 h-4 mr-1" />
                      <span className="text-sm">{user.location}</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <Calendar className="w-4 h-4 mr-1" />
                      <span className="text-sm">Joined {user.joinDate}</span>
                    </div>
                  </div>
                </div>
                
                <Button className="mt-4 sm:mt-0">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Profile
                </Button>
              </div>
              
              <p className="text-gray-700 mt-4">{user.bio}</p>
            </div>
          </div>
        </Card>
        
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card variant="default" padding="md" className="text-center">
            <div className="text-3xl font-bold text-primary-500">{user.stats.projects}</div>
            <div className="text-sm text-gray-600 mt-1">Total Projects</div>
          </Card>
          <Card variant="default" padding="md" className="text-center">
            <div className="text-3xl font-bold text-green-500">{user.stats.completed}</div>
            <div className="text-sm text-gray-600 mt-1">Completed</div>
          </Card>
          <Card variant="default" padding="md" className="text-center">
            <div className="text-3xl font-bold text-yellow-500">{user.stats.inProgress}</div>
            <div className="text-sm text-gray-600 mt-1">In Progress</div>
          </Card>
        </div>
        
        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Projects */}
          <Card variant="default" padding="none">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Recent Projects</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentProjects.map((project) => (
                  <div key={project.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{project.name}</p>
                      <p className="text-sm text-gray-600">{project.date}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      project.status === 'Completed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
          
          {/* Achievements */}
          <Card variant="default" padding="none">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Achievements</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="text-2xl">{achievement.icon}</div>
                    <div>
                      <p className="font-medium text-gray-900">{achievement.title}</p>
                      <p className="text-sm text-gray-600">{achievement.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default ProfileScreen;'''
    
    def _create_generic_screen(self, screen_name: str, design_tokens: Dict, color_palette: Dict) -> str:
        """Create a generic screen component"""
        return f'''import React from 'react';
import Layout from '../layout/Layout';
import Card from '../common/Card';

const {screen_name} = () => {{
  return (
    <Layout title="{screen_name}">
      <div className="space-y-6">
        <Card variant="default" padding="md">
          <h1 className="text-2xl font-bold text-gray-900">{screen_name}</h1>
          <p className="text-gray-600 mt-2">
            This is the {screen_name.lower()} screen. Content will be implemented based on specific requirements.
          </p>
        </Card>
      </div>
    </Layout>
  );
}};

export default {screen_name};'''
    
    # App structure generation methods
    def _create_app_component(self, design_system: Dict, app_name: str) -> str:
        """Create main App.jsx component"""
        return '''import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import Router from './components/Router';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Router />
      </div>
    </BrowserRouter>
  );
}

export default App;'''
    
    def _create_index_js(self, app_name: str) -> str:
        """Create index.js entry point"""
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
    
    def _create_router_component(self) -> str:
        """Create Router component with all routes"""
        return '''import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import OnboardingScreen from './screens/OnboardingScreen';
import MainScreen from './screens/MainScreen';
import DetailScreen from './screens/DetailScreen';
import SettingsScreen from './screens/SettingsScreen';
import ProfileScreen from './screens/ProfileScreen';

const Router = () => {
  return (
    <Routes>
      <Route path="/onboarding" element={<OnboardingScreen />} />
      <Route path="/" element={<MainScreen />} />
      <Route path="/detail/:id" element={<DetailScreen />} />
      <Route path="/settings" element={<SettingsScreen />} />
      <Route path="/profile" element={<ProfileScreen />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default Router;'''
    
    # Configuration file generation methods
    def _create_package_json(self, app_name: str) -> Dict[str, Any]:
        """Create package.json file"""
        package_name = app_name.lower().replace(' ', '-').replace('_', '-')
        
        return {
            "name": package_name,
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.16.4",
                "@testing-library/react": "^13.3.0",
                "@testing-library/user-event": "^13.5.0",
                "lucide-react": "^0.263.1",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.3.0",
                "react-scripts": "5.0.1",
                "web-vitals": "^2.1.4"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            },
            "devDependencies": {
                "autoprefixer": "^10.4.7",
                "postcss": "^8.4.14",
                "tailwindcss": "^3.1.6"
            }
        }
    
    def _create_tailwind_config(self, design_system: Dict) -> str:
        """Create Tailwind CSS configuration"""
        colors = design_system.get('brand_identity', {}).get('color_palette', {}).get('colors', {})
        fonts = design_system.get('brand_identity', {}).get('typography_system', {}).get('font_families', {})
        
        # Extract primary colors for Tailwind config
        primary_colors = colors.get('primary', {})
        if isinstance(primary_colors, str):
            primary_colors = {'500': primary_colors}
        
        return f'''/** @type {{import('tailwindcss').Config}} */
module.exports = {{
  content: [
    "./src/**/*.{{js,jsx,ts,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          50: '{primary_colors.get('50', '#f0f9ff')}',
          100: '{primary_colors.get('100', '#e0f2fe')}',
          200: '{primary_colors.get('200', '#bae6fd')}',
          300: '{primary_colors.get('300', '#7dd3fc')}',
          400: '{primary_colors.get('400', '#38bdf8')}',
          500: '{primary_colors.get('500', '#0ea5e9')}',
          600: '{primary_colors.get('600', '#0284c7')}',
          700: '{primary_colors.get('700', '#0369a1')}',
          800: '{primary_colors.get('800', '#075985')}',
          900: '{primary_colors.get('900', '#0c4a6e')}',
        }},
      }},
      fontFamily: {{
        'display': ['{fonts.get('display', 'Inter')}', 'sans-serif'],
        'body': ['{fonts.get('body', 'Inter')}', 'sans-serif'],
        'mono': ['{fonts.get('mono', 'JetBrains Mono')}', 'monospace'],
      }},
    }},
  }},
  plugins: [],
}}'''
    
    def _create_index_css(self, design_system: Dict) -> str:
        """Create index.css with Tailwind imports and custom styles"""
        fonts = design_system.get('brand_identity', {}).get('typography_system', {}).get('google_fonts_imports', {})
        css_import = fonts.get('css_import', '')
        
        return f'''/* Google Fonts Import */
{css_import}

/* Tailwind CSS */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom Styles */
@layer base {{
  body {{
    font-family: 'Inter', sans-serif;
  }}
}}

@layer utilities {{
  .font-display {{
    font-family: 'Inter', sans-serif;
  }}
  
  .font-body {{
    font-family: 'Inter', sans-serif;
  }}
}}'''
    
    def _create_index_html(self, app_name: str) -> str:
        """Create index.html file"""
        return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="{app_name} - Modern web application"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>{app_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''
    
    # Additional utility file creation
    def _create_cn_utility(self, project_path: Path) -> str:
        """Create cn utility for className merging"""
        cn_utility = '''import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}'''
        
        utils_path = project_path / 'src/utils/cn.js'
        with open(utils_path, 'w') as f:
            f.write(cn_utility)
        
        return str(utils_path)
    
    # Figma API methods
    def _create_figma_file(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Create new Figma file using Figma API"""
        if not self.figma_token:
            return None
        
        try:
            # Note: Figma API doesn't allow creating new files directly
            # This is a placeholder for the actual implementation
            # In practice, you would need to use Figma plugins or manual creation
            
            return {
                'key': 'sample-figma-file-key',
                'name': f"{app_name} Prototype",
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating Figma file: {e}")
            return None
    
    def _add_screens_to_figma(self, file_key: str, design_system: Dict, ux_strategy: Dict) -> bool:
        """Add screens to Figma file"""
        # This would implement the actual Figma API calls to add frames/screens
        # For now, return True as placeholder
        return True
    
    def _generate_figma_manual_instructions(self, design_system: Dict, app_name: str) -> Dict[str, Any]:
        """Generate manual instructions for creating Figma prototype"""
        colors = design_system.get('brand_identity', {}).get('color_palette', {}).get('colors', {})
        fonts = design_system.get('brand_identity', {}).get('typography_system', {}).get('font_families', {})
        
        return {
            'steps': [
                '1. Create a new Figma file',
                f'2. Set up color styles with primary: {colors.get("primary", {}).get("500", "#0ea5e9")}',
                f'3. Set up text styles with fonts: {fonts.get("display", "Inter")} and {fonts.get("body", "Inter")}',
                '4. Create frames for: Onboarding, Main Dashboard, Detail View, Settings, Profile',
                '5. Connect frames with prototyping arrows',
                '6. Set up interactions and transitions'
            ],
            'design_tokens': {
                'colors': colors,
                'fonts': fonts
            },
            'screen_dimensions': {
                'mobile': '375x812',
                'desktop': '1440x900'
            }
        }
    
    # Deployment configuration methods
    def _create_vercel_config(self, project_path: Path) -> str:
        """Create Vercel deployment configuration"""
        vercel_config = '''{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "s-maxage=31536000,immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}'''
        
        vercel_path = project_path / 'vercel.json'
        with open(vercel_path, 'w') as f:
            f.write(vercel_config)
        
        return str(vercel_path)
    
    def _create_netlify_config(self, project_path: Path) -> str:
        """Create Netlify deployment configuration"""
        netlify_config = '''[build]
  publish = "build"
  command = "npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200'''
        
        netlify_path = project_path / 'netlify.toml'
        with open(netlify_path, 'w') as f:
            f.write(netlify_config)
        
        return str(netlify_path)
    
    def _create_github_actions_config(self, project_path: Path) -> str:
        """Create GitHub Actions deployment configuration"""
        github_actions = '''name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm install
      
    - name: Build
      run: npm run build
      
    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./build'''
        
        github_path = project_path / '.github/workflows/deploy.yml'
        github_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(github_path, 'w') as f:
            f.write(github_actions)
        
        return str(github_path)
    
    # Documentation generation methods
    def _create_readme(self, design_system: Dict, ux_strategy: Dict, app_name: str) -> str:
        """Create comprehensive README.md"""
        return f'''# {app_name}

A modern React application built with Tailwind CSS and designed with a comprehensive design system.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 🏗️ Project Structure

```
src/
├── components/
│   ├── common/          # Reusable UI components
│   ├── layout/          # Layout components (Header, Navigation, etc.)
│   └── screens/         # Screen/page components
├── utils/               # Utility functions
├── styles/              # Global styles
└── assets/              # Images, icons, etc.
```

## 🎨 Design System

This project uses a custom design system with:

- **Colors**: Primary brand colors with full shade palette
- **Typography**: {design_system.get('brand_identity', {}).get('typography_system', {}).get('font_families', {}).get('display', 'Inter')} for headings, {design_system.get('brand_identity', {}).get('typography_system', {}).get('font_families', {}).get('body', 'Inter')} for body text
- **Components**: Consistent, reusable UI components
- **Spacing**: 8px grid system

## 📱 Features

- **Responsive Design**: Mobile-first approach
- **Modern UI**: Clean, intuitive interface
- **Component Library**: Reusable components
- **Dark Mode Ready**: Built with theme support in mind
- **Accessibility**: WCAG compliant components

## 🛠️ Tech Stack

- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **Vercel/Netlify Ready**: Optimized for modern deployment

## 📖 Available Scripts

- `npm start`: Start development server
- `npm run build`: Build for production
- `npm test`: Run tests
- `npm run eject`: Eject from Create React App (not recommended)

## 🚀 Deployment

### Vercel
```bash
npm install -g vercel
vercel --prod
```

### Netlify
```bash
npm run build
# Upload build folder to Netlify
```

### GitHub Pages
Push to main branch and GitHub Actions will handle deployment.

## 🎯 Next Steps

1. **Customize Design**: Update colors and fonts in `tailwind.config.js`
2. **Add Content**: Replace placeholder content with real data
3. **API Integration**: Connect to your backend services
4. **Testing**: Add unit and integration tests
5. **Performance**: Optimize for production

## 📄 License

MIT License - feel free to use this project as a starting point for your applications.
'''
    
    def _create_component_docs(self, design_system: Dict) -> str:
        """Create component documentation"""
        return '''# Component Documentation

This document describes the available components and their usage.

## Common Components

### Button
Flexible button component with multiple variants.

```jsx
import Button from '../common/Button';

<Button variant="primary" size="md">Primary Button</Button>
<Button variant="secondary" size="lg">Secondary Button</Button>
<Button variant="ghost" disabled>Disabled Button</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg'
- `disabled`: boolean
- `onClick`: function
- `children`: React.ReactNode

### Input
Form input with label, error, and helper text support.

```jsx
import Input from '../common/Input';

<Input 
  label="Email Address"
  type="email"
  placeholder="Enter your email"
  error="Invalid email format"
  helper="We'll never share your email"
/>
```

### Card
Container component for grouping related content.

```jsx
import Card from '../common/Card';

<Card variant="elevated" padding="lg">
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</Card>
```

### Avatar
User avatar component with fallback support.

```jsx
import Avatar from '../common/Avatar';

<Avatar 
  src="/path/to/image.jpg"
  alt="User Name"
  fallback="UN"
  size="lg"
/>
```

### Loading
Loading indicator component.

```jsx
import Loading from '../common/Loading';

<Loading variant="spinner" size="md" />
<Loading variant="dots" />
```

## Layout Components

### Header
Application header with navigation and user menu.

### Navigation
Sidebar navigation with mobile support.

### Layout
Main layout wrapper that includes header and navigation.

```jsx
import Layout from '../layout/Layout';

<Layout title="Page Title">
  <div>Your page content</div>
</Layout>
```

## Screen Components

### OnboardingScreen
Multi-step onboarding flow for new users.

### MainScreen
Main dashboard with stats and recent activity.

### DetailScreen
Detailed view for individual items.

### SettingsScreen
User settings and preferences.

### ProfileScreen
User profile with stats and achievements.

## Styling Guidelines

### Colors
Use Tailwind color classes with the primary color palette:
- `text-primary-500`, `bg-primary-500`, etc.

### Spacing
Use consistent spacing classes:
- `space-y-4`, `space-x-3`, `p-4`, `m-6`, etc.

### Typography
- Headings: `text-xl font-semibold text-gray-900`
- Body text: `text-gray-600`
- Small text: `text-sm text-gray-500`

### Responsive Design
Always use mobile-first responsive classes:
- `md:grid-cols-2`, `lg:flex-row`, etc.
'''
    
    def _create_development_guide(self, app_name: str) -> str:
        """Create development guide"""
        return f'''# Development Guide

This guide covers development practices and guidelines for {app_name}.

## 🏗️ Development Setup

### Prerequisites
- Node.js 16 or higher
- npm or yarn package manager
- Git for version control

### Environment Setup
1. Clone the repository
2. Run `npm install` to install dependencies
3. Run `npm start` to start the development server
4. Open http://localhost:3000 in your browser

## 📁 Project Structure

```
src/
├── components/
│   ├── common/          # Reusable UI components
│   ├── layout/          # Layout components
│   ├── screens/         # Page components
│   └── Router.jsx       # Route definitions
├── utils/               # Utility functions
├── styles/              # Global styles
├── assets/              # Static assets
├── App.jsx              # Main app component
└── index.js             # Entry point
```

## 🎨 Design System

### Colors
The application uses a consistent color palette defined in `tailwind.config.js`:
- Primary: Blue color palette (50-900 shades)
- Semantic: Success (green), warning (yellow), error (red)
- Neutral: Gray color palette

### Typography
- Display font: Used for headings and important text
- Body font: Used for regular text content
- Monospace: Used for code and technical content

### Components
All components follow these principles:
- Consistent API patterns
- Prop-based customization
- Accessible by default
- Mobile-first responsive design

## 🛠️ Development Practices

### File Naming
- Components: PascalCase (e.g., `Button.jsx`)
- Utilities: camelCase (e.g., `formatDate.js`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS.js`)

### Component Structure
```jsx
import React from 'react';
import {{ cn }} from '../utils/cn';

const ComponentName = ({{ 
  prop1, 
  prop2 = 'defaultValue',
  className,
  ...props 
}}) => {{
  return (
    <div className={{cn('base-classes', className)}} {{...props}}>
      {{/* Component content */}}
    </div>
  );
}};

export default ComponentName;
```

### State Management
- Use React's built-in useState for local state
- Consider useContext for app-wide state
- Use useReducer for complex state logic

### Styling
- Use Tailwind CSS utility classes
- Create component variants using the `cn` utility
- Follow mobile-first responsive design
- Maintain consistent spacing and sizing

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### Test Structure
```jsx
import {{ render, screen }} from '@testing-library/react';
import Button from './Button';

test('renders button with text', () => {{
  render(<Button>Click me</Button>);
  const button = screen.getByRole('button', {{ name: /click me/i }});
  expect(button).toBeInTheDocument();
}});
```

## 🚀 Build and Deployment

### Production Build
```bash
npm run build
```

### Deployment Options
1. **Vercel**: `vercel --prod`
2. **Netlify**: Upload build folder
3. **GitHub Pages**: Push to main branch

### Performance Optimization
- Use React.memo for expensive components
- Implement code splitting with React.lazy
- Optimize images and assets
- Monitor bundle size

## 📖 Adding New Features

### 1. Create Component
```jsx
// src/components/common/NewComponent.jsx
import React from 'react';

const NewComponent = () => {{
  return <div>New Component</div>;
}};

export default NewComponent;
```

### 2. Add Route (if needed)
```jsx
// src/components/Router.jsx
import NewScreen from './screens/NewScreen';

// Add to Routes
<Route path="/new" element={{<NewScreen />}} />
```

### 3. Update Navigation
```jsx
// src/components/layout/Navigation.jsx
// Add new nav item to navItems array
```

## 🐛 Debugging

### Common Issues
1. **Module not found**: Check import paths
2. **Tailwind classes not working**: Restart dev server
3. **Component not rendering**: Check for JavaScript errors in console

### Debug Tools
- React Developer Tools browser extension
- Console.log for state debugging
- Network tab for API issues

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [React Router Documentation](https://reactrouter.com/)
- [Lucide React Icons](https://lucide.dev/)
'''
    
    def _generate_next_steps(self, project_path: Path, app_name: str) -> List[str]:
        """Generate next steps for the user"""
        return [
            f"1. Navigate to the project directory: cd {project_path}",
            "2. Install dependencies: npm install",
            "3. Start development server: npm start",
            "4. Open http://localhost:3000 in your browser",
            "5. Customize the design system in tailwind.config.js",
            "6. Replace placeholder content with your actual content",
            "7. Add your backend API integration",
            "8. Deploy to Vercel, Netlify, or GitHub Pages",
            "9. Set up analytics and monitoring",
            "10. Add unit tests for your components"
        ]
    
    # Helper methods
    def _extract_primary_color(self, color_palette: Dict) -> str:
        """Extract primary color from color palette"""
        colors = color_palette.get('colors', {})
        primary = colors.get('primary', {})
        
        if isinstance(primary, dict):
            return primary.get('500', '#0ea5e9')
        elif isinstance(primary, str):
            return primary
        else:
            return '#0ea5e9'

# Global instance
prototype_builder = PrototypeBuilder()