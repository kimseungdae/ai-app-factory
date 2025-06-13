#!/usr/bin/env python3
"""
Test script for DesignSystemGenerator
Shows how to use the DesignSystemGenerator to create complete design systems
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.design_system_generator import design_system_generator
from agents.ux_researcher import ux_researcher
import json
from datetime import datetime

def test_design_system_generation():
    """Test the design system generation functionality"""
    print("🎨 Testing DesignSystemGenerator...")
    print("=" * 60)
    
    # First, create sample UX analysis data (or use real data from UXResearcher)
    sample_ux_analysis = create_sample_ux_analysis()
    
    print(f"\n📊 Input UX Analysis:")
    print(f"   Trend: {sample_ux_analysis['trend_keyword']}")
    print(f"   Category: {sample_ux_analysis['category']}")
    print(f"   Primary Persona: {sample_ux_analysis['personas'][0]['name']}")
    
    # Generate complete design system
    print(f"\n🎨 Generating complete design system...")
    design_system = design_system_generator.generate_complete_design_system(sample_ux_analysis)
    
    if 'error' in design_system:
        print(f"❌ Error: {design_system['error']}")
        return
    
    print(f"✅ Design system generated successfully!")
    
    # Display key components
    display_design_system_overview(design_system)
    
    # Save to files
    save_design_system_files(design_system, sample_ux_analysis['trend_keyword'])
    
    # Show implementation examples
    show_implementation_examples(design_system)

def create_sample_ux_analysis():
    """Create sample UX analysis data for testing"""
    return {
        'trend_keyword': 'AI fitness',
        'category': 'health',
        'personas': [
            {
                'name': '바쁜 직장인 김현수',
                'age': 28,
                'occupation': '마케팅 담당자',
                'motivations': ['효율성', '건강', '간편함'],
                'pain_points': ['시간 부족', '복잡한 운동 계획'],
                'tech_savviness': '중급'
            },
            {
                'name': '운동 초보자 이지은',
                'age': 24,
                'occupation': '대학생',
                'motivations': ['건강한 습관', '자신감', '즐거움'],
                'pain_points': ['운동 지식 부족', '동기 부족'],
                'tech_savviness': '고급'
            }
        ],
        'ux_strategy': {
            'strategies': [
                {
                    'direction': '원터치 간편 사용',
                    'core_concept': '5초 내 운동 시작',
                    'target_persona': '바쁜 직장인',
                    'key_features': ['즉시 시작', '자동 추천', '진행 상황 추적'],
                    'differentiation': '기존 앱 대비 80% 더 간단한 시작 과정'
                }
            ],
            'design_principles': [
                '최소한의 터치로 최대 효과',
                '시각적 진행 상황 표시',
                '동기 부여하는 디자인'
            ]
        },
        'user_needs': {
            'key_insights': [
                '사용자들은 간편함을 최우선으로 생각함',
                'AI의 개인화 추천을 신뢰함',
                '즉시 보이는 결과를 원함'
            ]
        }
    }

def display_design_system_overview(design_system):
    """Display key aspects of the generated design system"""
    print(f"\n🎯 Design System Overview:")
    print("-" * 50)
    
    # Metadata
    metadata = design_system.get('metadata', {})
    print(f"📋 Generated for: {metadata.get('generated_for', 'Unknown')}")
    print(f"🏷️  Category: {metadata.get('category', 'Unknown')}")
    print(f"👤 Target Persona: {metadata.get('target_persona', 'Unknown')}")
    
    # Brand Identity
    brand_identity = design_system.get('brand_identity', {})
    
    # Color Palette
    color_palette = brand_identity.get('color_palette', {})
    if color_palette:
        print(f"\n🎨 Color Palette:")
        colors = color_palette.get('colors', {})
        
        if 'primary' in colors:
            primary = colors['primary']
            if isinstance(primary, dict):
                print(f"   Primary: {primary.get('500', 'N/A')}")
            else:
                print(f"   Primary: {primary}")
        
        if 'semantic' in colors:
            semantic = colors['semantic']
            print(f"   Success: {semantic.get('success', 'N/A')}")
            print(f"   Warning: {semantic.get('warning', 'N/A')}")
            print(f"   Error: {semantic.get('error', 'N/A')}")
        
        psychology = color_palette.get('psychology', {})
        if psychology:
            print(f"   🧠 Psychology: {psychology.get('target_emotion', 'N/A')}")
    
    # Typography
    typography = brand_identity.get('typography_system', {})
    if typography:
        print(f"\n✍️  Typography:")
        font_families = typography.get('font_families', {})
        print(f"   Display Font: {font_families.get('display', 'N/A')}")
        print(f"   Body Font: {font_families.get('body', 'N/A')}")
        print(f"   Mono Font: {font_families.get('mono', 'N/A')}")
    
    # Icon System
    icon_system = design_system.get('icon_system', {})
    if icon_system:
        print(f"\n🔸 Icon System:")
        print(f"   Primary Library: {icon_system.get('primary_library', 'N/A')}")
        categories = icon_system.get('categories', {})
        print(f"   Categories: {', '.join(categories.keys())}")
    
    # Component System
    component_system = design_system.get('component_system', {})
    if component_system:
        print(f"\n🧩 Components:")
        components = component_system.get('components', {})
        print(f"   Available: {', '.join(components.keys())}")
        
        principles = component_system.get('design_principles', [])
        if principles:
            print(f"   Design Principles:")
            for principle in principles[:3]:
                print(f"     • {principle}")
    
    # Figma Resources
    figma_resources = design_system.get('figma_resources', {})
    if figma_resources:
        templates = figma_resources.get('recommended_templates', [])
        print(f"\n🎭 Figma Templates: {len(templates)} recommended")
        if templates:
            top_template = templates[0]
            print(f"   Top: {top_template.get('name', 'N/A')}")
            print(f"   Components: {top_template.get('components', 'N/A')}")
            print(f"   Rating: {top_template.get('rating', 'N/A')}")

def save_design_system_files(design_system, trend_keyword):
    """Save design system to multiple output files"""
    print(f"\n💾 Saving design system files...")
    
    # Main design system JSON
    main_filename = f"design_system_{trend_keyword.replace(' ', '_')}.json"
    with open(main_filename, 'w', encoding='utf-8') as f:
        json.dump(design_system, f, indent=2, ensure_ascii=False)
    print(f"   📄 Complete system: {main_filename}")
    
    # CSS Variables file
    implementation = design_system.get('implementation', {})
    css_variables = implementation.get('css_variables', '')
    if css_variables:
        css_filename = f"design_tokens_{trend_keyword.replace(' ', '_')}.css"
        with open(css_filename, 'w') as f:
            f.write(css_variables)
        print(f"   🎨 CSS Variables: {css_filename}")
    
    # Tailwind Config
    tailwind_config = implementation.get('tailwind_config', {})
    if tailwind_config:
        tailwind_filename = f"tailwind_config_{trend_keyword.replace(' ', '_')}.json"
        with open(tailwind_filename, 'w', encoding='utf-8') as f:
            json.dump(tailwind_config, f, indent=2, ensure_ascii=False)
        print(f"   🌪️  Tailwind Config: {tailwind_filename}")
    
    # React Theme
    react_theme = implementation.get('react_theme', {})
    if react_theme:
        react_filename = f"react_theme_{trend_keyword.replace(' ', '_')}.json"
        with open(react_filename, 'w', encoding='utf-8') as f:
            json.dump(react_theme, f, indent=2, ensure_ascii=False)
        print(f"   ⚛️  React Theme: {react_filename}")
    
    print(f"   ✅ All files saved successfully!")

def show_implementation_examples(design_system):
    """Show practical implementation examples"""
    print(f"\n🛠️  Implementation Examples:")
    print("-" * 50)
    
    # CSS Variables example
    implementation = design_system.get('implementation', {})
    css_variables = implementation.get('css_variables', '')
    if css_variables:
        print(f"\n📝 CSS Variables (first few lines):")
        lines = css_variables.split('\n')[:8]
        for line in lines:
            if line.strip():
                print(f"   {line}")
        if len(css_variables.split('\n')) > 8:
            print(f"   ... (see full file for complete variables)")
    
    # Component examples
    component_system = design_system.get('component_system', {})
    components = component_system.get('components', {})
    
    if 'buttons' in components:
        button_tailwind = components['buttons'].get('tailwind_classes', {})
        if button_tailwind:
            print(f"\n🔘 Button Component Examples:")
            for variant, classes in button_tailwind.items():
                print(f"   {variant.title()}: {classes}")
    
    # Icon usage examples
    icon_system = design_system.get('icon_system', {})
    implementation_examples = icon_system.get('implementation', {})
    if implementation_examples:
        usage_examples = implementation_examples.get('usage_examples', {})
        print(f"\n🔸 Icon Usage Examples:")
        for framework, example in usage_examples.items():
            print(f"   {framework.title()}: {example}")
    
    # Google Fonts imports
    brand_identity = design_system.get('brand_identity', {})
    typography = brand_identity.get('typography_system', {})
    google_fonts = typography.get('google_fonts_imports', {})
    if google_fonts:
        print(f"\n✍️  Google Fonts Import:")
        css_import = google_fonts.get('css_import', '')
        if css_import:
            print(f"   CSS: {css_import}")

def test_with_real_ux_data():
    """Test with real UX analysis data from UXResearcher"""
    print(f"\n🔄 Testing with Real UX Data:")
    print("-" * 40)
    
    if not ux_researcher.enabled:
        print("⚠️  UXResearcher is disabled - using sample data")
        return
    
    # Generate real UX analysis
    print("📊 Generating UX analysis for 'productivity app'...")
    ux_analysis = ux_researcher.analyze_ux_for_trend('productivity app', 'productivity')
    
    if 'error' in ux_analysis:
        print(f"❌ UX Analysis failed: {ux_analysis['error']}")
        return
    
    print("✅ UX analysis completed!")
    
    # Generate design system from real data
    print("🎨 Generating design system from real UX data...")
    design_system = design_system_generator.generate_complete_design_system(ux_analysis)
    
    if 'error' not in design_system:
        print("✅ Design system generated from real data!")
        
        # Quick overview
        metadata = design_system.get('metadata', {})
        print(f"   Generated for: {metadata.get('generated_for', 'Unknown')}")
        print(f"   Target: {metadata.get('target_persona', 'Unknown')}")
        
        # Save
        save_design_system_files(design_system, 'productivity_app_real_data')
    else:
        print(f"❌ Design system generation failed: {design_system['error']}")

def show_design_system_benefits():
    """Show the benefits and next steps for using the design system"""
    print(f"\n🎯 Design System Benefits:")
    print("-" * 40)
    
    benefits = [
        "🎨 Consistent visual identity across all touchpoints",
        "⚡ Faster development with pre-defined components",
        "♿ Built-in accessibility standards and guidelines",
        "📱 Responsive design patterns for all screen sizes",
        "🔄 Easy maintenance and updates across the system",
        "👥 Clear guidelines for designers and developers",
        "🚀 Professional appearance that builds user trust"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print(f"\n🛠️  Next Steps:")
    print("-" * 20)
    
    steps = [
        "1. 📋 Review generated design tokens and customize as needed",
        "2. 🎭 Download recommended Figma templates and apply your colors",
        "3. 💻 Implement CSS variables or Tailwind config in your project",
        "4. 🧩 Build components using the provided specifications",
        "5. 🧪 Test designs with real users and iterate",
        "6. 📚 Document usage guidelines for your team"
    ]
    
    for step in steps:
        print(f"   {step}")

if __name__ == "__main__":
    print("🎨 DesignSystemGenerator Test Suite")
    print("=" * 60)
    
    # Check configuration
    print("\n⚙️  Configuration Check:")
    print(f"   DesignSystemGenerator enabled: {design_system_generator.enabled}")
    
    if design_system_generator.enabled:
        try:
            # Main test with sample data
            test_design_system_generation()
            
            # Test with real UX data if available
            test_with_real_ux_data()
            
            # Show benefits and next steps
            show_design_system_benefits()
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("💡 Check your configuration and dependencies")
    else:
        print("⚠️  DesignSystemGenerator is disabled. Check config/settings.yaml")
        print("💡 Showing design system benefits anyway...")
        show_design_system_benefits()
    
    print("\n✅ Test complete!")
    print(f"\n🎉 You now have a complete design system generator that:")
    print(f"   🎨 Creates brand-aligned color palettes")
    print(f"   ✍️  Selects perfect font combinations")
    print(f"   🔸 Provides consistent icon systems")
    print(f"   🧩 Generates component specifications")
    print(f"   🎭 Recommends Figma templates")
    print(f"   💻 Outputs ready-to-use code!")
    
    print(f"\n📚 Usage in your code:")
    print("```python")
    print("from agents.design_system_generator import design_system_generator")
    print("from agents.ux_researcher import ux_researcher")
    print("")
    print("# Get UX analysis")
    print("ux_data = ux_researcher.analyze_ux_for_trend('your_trend', 'category')")
    print("")
    print("# Generate complete design system")
    print("design_system = design_system_generator.generate_complete_design_system(ux_data)")
    print("")
    print("# Use the results")
    print("colors = design_system['brand_identity']['color_palette']")
    print("components = design_system['component_system']")
    print("tokens = design_system['design_tokens']")
    print("```")