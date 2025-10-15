description: MUST BE APPLIED WHEN working on development workflow, version control, and development process.
applyTo: "**/.github/**/*,**/.gitignore,**/scripts/**/*,**/Makefile"
alwaysApply: false

# Development Workflow Guidelines: Blind Style Model

## Development Philosophy

**Methodology**: Agile com RIPER Framework
**Git Strategy**: Feature branches + Pull Requests
**Documentation**: Inline docstrings + memory-bank

### Core Values
- **Acessibilidade**: Pensar sempre no usuário com deficiência visual
- **Reprodutibilidade**: Garantir determinismo em embeddings e processamento
- **Colaboração**: Documentação clara e código legível
- **Continuous Improvement**: Refatoração constante

## Version Control Workflow

### Branching Strategy [Trunk Base Git]

### Branch Naming Conventions
```bash
# Features
feature/feature-brief-description

# Bugfixes
bugfix/bug-brief-description
```

### Commit Message Format [Follow Convetional Git Commits]
**Types**:
- `feat`: Nova feature (ex: `feat(embeddings): add embedding validation`)
- `fix`: Bug fix (ex: `fix(vector_db): resolve connection leak`)
- `docs`: Documentação (ex: `docs(readme): update setup instructions`)
- `style`: Formatação (ex: `style(embeddings): apply black formatter`)
- `refactor`: Refatoração (ex: `refactor(main): extract pipeline functions`)
- `test`: Testes (ex: `test(embeddings): add hash_embedding tests`)
- `chore`: Manutenção (ex: `chore(deps): update chromadb to 1.1.2`)

### Pull Request Process 

#### PR Template
```markdown
## Description
[Descrição clara das mudanças]

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- [Mudança 1]
- [Mudança 2]
- [Mudança 3]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added ONLY for complex logic
- [ ] Documentation updated (if needed)
- [ ] No merge conflicts
- [ ] Type hints added to public methods
- [ ] Docstrings updated
- [ ] Review with DL
```


---
*Development workflow guidelines for Blind Style Model using GitHub Copilot*
