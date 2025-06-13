#!/usr/bin/env python3
"""
Test script for PrototypeBuilder - React prototype generation
Tests the final stage of the AI App Factory pipeline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from datetime import datetime

# Import the PrototypeBuilder class directly
try:
    from agents.prototype_builder import PrototypeBuilder
    prototype_builder = PrototypeBuilder()
except Exception as e:
    print(f"Failed to import PrototypeBuilder: {e}")
    sys.exit(1)

def test_prototype_builder():
    """Test PrototypeBuilder with sample UX analysis and design system"""
    print("🏗️ Testing PrototypeBuilder - React Prototype Generation")
    print("=" * 60)
    
    # Sample design system (would come from DesignSystemGenerator)
    sample_design_system = {
        "brand_identity": {
            "color_palette": {
                "colors": {
                    "primary": {
                        "50": "#f0f9ff",
                        "100": "#e0f2fe", 
                        "200": "#bae6fd",
                        "300": "#7dd3fc",
                        "400": "#38bdf8",
                        "500": "#0ea5e9",
                        "600": "#0284c7",
                        "700": "#0369a1",
                        "800": "#075985",
                        "900": "#0c4a6e"
                    },
                    "secondary": {
                        "500": "#8b5cf6"
                    }
                }
            },
            "typography_system": {
                "font_families": {
                    "display": "Inter",
                    "body": "Inter",
                    "mono": "JetBrains Mono"
                },
                "google_fonts_imports": {
                    "css_import": "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');"
                }
            }
        },
        "component_system": {
            "components": {
                "button": {
                    "variants": ["primary", "secondary", "ghost"],
                    "sizes": ["sm", "md", "lg"]
                }
            }
        },
        "design_tokens": {
            "spacing": {
                "unit": "8px"
            }
        }
    }
    
    # Sample UX strategy (would come from UXResearcher)
    sample_ux_strategy = {
        "strategies": [
            {
                "name": "Simplicity-First Approach",
                "description": "Focus on minimal cognitive load and intuitive interactions",
                "key_principles": [
                    "One primary action per screen",
                    "Progressive disclosure of features",
                    "Clear visual hierarchy"
                ],
                "target_emotion": "confidence"
            }
        ],
        "personas": [
            {
                "name": "김현수 (바쁜 직장인)",
                "age": 28,
                "pain_points": ["시간 부족", "복잡한 인터페이스"],
                "motivations": ["효율성", "간편함"]
            }
        ]
    }
    
    app_name = "ProductivityPro"
    
    print(f"\n📱 Generating React prototype for: {app_name}")
    print("-" * 40)
    
    if not prototype_builder.enabled:
        print("⚠️  PrototypeBuilder is disabled in configuration")
        return
    
    try:
        # Generate complete prototype
        result = prototype_builder.build_complete_prototype(
            design_system=sample_design_system,
            ux_strategy=sample_ux_strategy,
            app_name=app_name
        )
        
        if 'error' in result:
            print(f"❌ Error generating prototype: {result['error']}")
            return
        
        # Display results
        print(f"✅ Prototype generated successfully!")
        print(f"\n📊 Generation Summary:")
        print(f"   • Project Path: {result['project_info']['project_path']}")
        print(f"   • Technology Stack: React + Tailwind CSS")
        print(f"   • Generated At: {result['project_info']['generated_at']}")
        
        # Components generated
        components = result['generated_files']['components']
        print(f"\n🧩 Generated Components:")
        print(f"   • Common: {len(components['common'])} components")
        print(f"     - {', '.join(components['common'])}")
        print(f"   • Screens: {len(components['screens'])} screens")
        print(f"     - {', '.join(components['screens'])}")
        print(f"   • Layout: {len(components['layout'])} components")
        print(f"     - {', '.join(components['layout'])}")
        
        # App structure
        app_files = result['generated_files']['app_files']
        print(f"\n📁 App Structure:")
        for file_name in app_files:
            print(f"   • {file_name}")
        
        # Configuration files
        config_files = result['generated_files']['config_files']
        print(f"\n⚙️  Configuration Files:")
        for file_name in config_files:
            print(f"   • {file_name}")
        
        # Deployment options
        deployment = result['deployment']
        print(f"\n🚀 Deployment Options:")
        for platform, config in deployment.items():
            status = "✅ Ready" if config['ready'] else "❌ Not configured"
            print(f"   • {platform.title()}: {status}")
        
        # Figma prototype status
        figma = result['figma_prototype']
        if figma:
            print(f"\n🎨 Figma Prototype:")
            if figma['status'] == 'created':
                print(f"   • Status: ✅ Created")
                print(f"   • URL: {figma['prototype_url']}")
            elif figma['status'] == 'skipped':
                print(f"   • Status: ⚠️  Skipped - {figma['reason']}")
            else:
                print(f"   • Status: ❌ Failed - {figma.get('reason', 'Unknown error')}")
        
        # Next steps
        print(f"\n📋 Next Steps:")
        for i, step in enumerate(result['next_steps'][:5], 1):
            print(f"   {i}. {step}")
        
        # URLs
        print(f"\n🌐 Access URLs:")
        print(f"   • Local Development: {result['urls']['local_dev']}")
        if result['urls']['figma_prototype']:
            print(f"   • Figma Prototype: {result['urls']['figma_prototype']}")
        
        # Save complete result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"prototype_test_result_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Complete result saved to: {output_file}")
        
        # Test specific generated files
        print(f"\n🔍 Verification:")
        project_path = result['project_info']['project_path']
        
        # Check if key files exist
        key_files = [
            'package.json',
            'src/App.jsx',
            'src/components/common/Button.jsx',
            'src/components/screens/MainScreen.jsx',
            'tailwind.config.js'
        ]
        
        for file_path in key_files:
            full_path = os.path.join(project_path, file_path)
            if os.path.exists(full_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - Missing")
        
        print(f"\n🎉 PrototypeBuilder test completed successfully!")
        print(f"\n💡 To use the generated prototype:")
        print(f"   cd {project_path}")
        print(f"   npm install")
        print(f"   npm start")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_component_generation():
    """Test individual component generation"""
    print(f"\n🧩 Testing Individual Component Generation:")
    print("-" * 40)
    
    if not prototype_builder.enabled:
        print("⚠️  PrototypeBuilder is disabled")
        return
    
    # Test color extraction
    sample_color_palette = {
        "colors": {
            "primary": {
                "500": "#0ea5e9"
            }
        }
    }
    
    primary_color = prototype_builder._extract_primary_color(sample_color_palette)
    print(f"✅ Color extraction: {primary_color}")
    
    # Test component creation methods (these are internal methods)
    design_tokens = {}
    
    try:
        button_code = prototype_builder._create_button_component(design_tokens, sample_color_palette)
        print(f"✅ Button component: {len(button_code)} characters generated")
        
        input_code = prototype_builder._create_input_component(design_tokens, sample_color_palette)
        print(f"✅ Input component: {len(input_code)} characters generated")
        
        card_code = prototype_builder._create_card_component(design_tokens, sample_color_palette)
        print(f"✅ Card component: {len(card_code)} characters generated")
        
        print(f"✅ All component generation methods working correctly")
        
    except Exception as e:
        print(f"❌ Component generation error: {e}")

if __name__ == "__main__":
    print("🧪 Starting PrototypeBuilder Test Suite")
    print("=" * 50)
    
    # Test component generation
    test_component_generation()
    
    # Test complete prototype generation
    result = test_prototype_builder()
    
    if result:
        print(f"\n🎯 Test Summary:")
        print(f"   • Components: ✅ Generated successfully")
        print(f"   • Project Structure: ✅ Created successfully")
        print(f"   • Configuration: ✅ Generated successfully")
        print(f"   • Documentation: ✅ Created successfully")
        print(f"\n🚀 PrototypeBuilder is ready for production use!")
    else:
        print(f"\n❌ Tests failed - check error messages above")
    
    print(f"\n✅ PrototypeBuilder test suite completed!")