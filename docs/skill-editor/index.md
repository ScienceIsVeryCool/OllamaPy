# Skill Editor

Interactive web-based interface for creating and managing OllamaPy skills.

## Overview

The Skill Editor provides a user-friendly web interface for creating, editing, and managing AI skills. It features:

- **Visual skill creation**: Interactive forms and builders
- **Real-time testing**: Test skills as you build them
- **Code generation**: Automatic skill file generation
- **Template library**: Pre-built skill templates
- **Validation**: Built-in skill validation and testing

## Accessing the Skill Editor

<div id="skill-editor-container">
    <div class="skill-editor-loading" style="text-align: center; padding: 40px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px;">
        <p>Loading skill editor interface...</p>
    </div>
</div>

<script>
// Detect if we're on GitHub Pages or running locally
const isGitHubPages = window.location.hostname === 'scienceisverycool.github.io';
const container = document.getElementById('skill-editor-container');

if (isGitHubPages) {
    // Show message for GitHub Pages visitors
    container.innerHTML = `
        <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #856404; margin-top: 0;">📝 Skill Editor - Local Only Feature</h3>
            <p style="color: #856404;">
                The interactive skill editor is only available when running OllamaPy locally.
                To use the skill editor:
            </p>
            <ol style="color: #856404;">
                <li>Install OllamaPy: <code>pip install ollamapy[editor]</code></li>
                <li>Run with skill editor: <code>ollamapy --skill-editor</code></li>
                <li>Open: <a href="http://localhost:5000" style="color: #856404;">http://localhost:5000</a></li>
            </ol>
            <p style="color: #856404; margin-bottom: 0;">
                The skill editor provides a complete visual interface for creating and managing AI skills.
            </p>
        </div>
    `;
} else {
    // Show iframe for local users
    container.innerHTML = `
        <iframe 
            src="http://localhost:5000" 
            width="100%" 
            height="800px" 
            style="border: 1px solid #ddd; border-radius: 8px; opacity: 0; transition: opacity 0.3s;"
            onload="this.style.opacity = '1'"
            onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
        ></iframe>
        <div style="display: none; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 20px; margin: 20px 0; color: #721c24;">
            <h4>Skill Editor Not Running</h4>
            <p>The skill editor server is not running. Start it with:</p>
            <code>ollamapy --skill-editor</code>
            <p>Then refresh this page.</p>
        </div>
    `;
}
</script>

## Features

### Visual Skill Builder
- **Drag-and-drop interface**: Build skills visually without coding
- **Parameter configuration**: Set up skill parameters with validation
- **Action mapping**: Map user intents to skill actions
- **Response templates**: Define how the skill responds to users

### Testing & Validation
- **Interactive testing**: Test skills in real-time as you build them
- **Vibe test integration**: Run consistency tests on your skills
- **Error checking**: Automatic validation of skill configuration
- **Performance metrics**: Monitor skill performance and accuracy

### Code Generation
- **Automatic JSON generation**: Generate skill files automatically
- **Template system**: Start from pre-built skill templates
- **Export options**: Export skills in various formats
- **Version control**: Track skill changes and versions

### Integration
- **Hot reload**: Skills update automatically in the chat interface
- **Skill registry**: Automatically register new skills
- **Dependency management**: Handle skill dependencies
- **Documentation**: Auto-generate skill documentation

## Getting Started Locally

1. **Install dependencies**:
   ```bash
   pip install flask flask-cors
   ```

2. **Start the skill editor**:
   ```bash
   ollamapy --skill-editor
   ```

3. **Open in browser**:
   Visit `http://localhost:5000`

4. **Create your first skill**:
   - Click "New Skill"
   - Fill in the skill details
   - Configure parameters and actions
   - Test your skill
   - Save and export

## Skill Development Workflow

1. **Plan**: Define what your skill should do
2. **Create**: Use the visual builder to create the skill
3. **Test**: Run tests to verify functionality
4. **Refine**: Adjust parameters and responses
5. **Deploy**: Export and integrate into your chat system
6. **Monitor**: Use vibe tests to monitor performance

## Advanced Features

### Custom Templates
Create reusable skill templates for common patterns:
- Data analysis skills
- API integration skills
- File manipulation skills
- Communication skills

### Batch Operations
- Create multiple skills at once
- Import/export skill collections
- Bulk testing and validation
- Batch updates and modifications

### Integration APIs
- REST API for programmatic access
- Webhook support for external triggers
- Plugin system for custom functionality
- Third-party service integration

## Troubleshooting

### Skill Editor Won't Start
- Ensure Flask dependencies are installed: `pip install flask flask-cors`
- Check if port 5000 is available
- Try a different port: `ollamapy --skill-editor --port 8080`

### Skills Not Loading
- Verify skill file syntax
- Check skill directory permissions
- Review error logs in the editor console
- Ensure skill registry is updated

### Performance Issues
- Clear browser cache
- Restart the skill editor server
- Check system resources
- Optimize skill complexity