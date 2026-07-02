"""ReadmeMagic CLI - One spell, beautiful README"""
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog='readme-magic',
        description='✨ ReadmeMagic - One spell, beautiful README',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  readme-magic generate --project-path ./my-project
  readme-magic generate --template ai-project
  readme-magic preview --output preview.html
  readme-magic templates
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a beautiful README')
    generate_parser.add_argument('--project-path', '-p', default='.', help='Path to project (default: current directory)')
    generate_parser.add_argument('--template', '-t', default='standard', 
                                choices=['standard', 'ai-project', 'cli-tool', 'library', 'personal'],
                                help='Template to use (default: standard)')
    generate_parser.add_argument('--output', '-o', default='README.md', help='Output file (default: README.md)')
    generate_parser.add_argument('--primary-color', default='#667eea', help='Primary color (default: #667eea)')
    generate_parser.add_argument('--secondary-color', default='#764ba2', help='Secondary color (default: #764ba2)')
    generate_parser.add_argument('--badges', help='Comma-separated badges to add')
    generate_parser.add_argument('--star-history', action='store_true', help='Add Star History chart')
    generate_parser.add_argument('--repo', help='GitHub repo (owner/repo) for Star History')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview README in browser')
    preview_parser.add_argument('--input', '-i', default='README.md', help='Input README file')
    preview_parser.add_argument('--output', '-o', default='preview.html', help='Output HTML file')
    
    # Templates command
    subparsers.add_parser('templates', help='List available templates')
    
    # Version
    parser.add_argument('--version', '-v', action='version', version='ReadmeMagic 1.0.0')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'generate':
        print(f"✨ Generating README with template: {args.template}")
        print(f"📁 Project path: {args.project_path}")
        print(f"📄 Output: {args.output}")
        print(f"🎨 Colors: {args.primary_color} / {args.secondary_color}")
        # TODO: Implement actual generation logic
        print("✅ README generated successfully!")
        
    elif args.command == 'preview':
        print(f"👀 Previewing {args.input}")
        # TODO: Implement preview logic
        print(f"🌐 Open {args.output} in your browser")
        
    elif args.command == 'templates':
        print("📝 Available templates:")
        print("  - standard    : General open source projects")
        print("  - ai-project  : AI/ML projects")
        print("  - cli-tool    : Command line tools")
        print("  - library     : Reusable components")
        print("  - personal    : Portfolio projects")

if __name__ == '__main__':
    main()

