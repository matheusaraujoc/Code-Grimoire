import os
import ast

def classify_file(filepath: str) -> str:
    """Usa heurísticas no caminho/nome do arquivo para deduzir seu papel no sistema."""
    name = os.path.basename(filepath).lower()
    path_lower = filepath.lower()

    if name in ['main.py', 'app.py', 'index.js', 'server.py', 'manage.py', 'run.py']:
        return "Entrypoint (Ponto de Entrada / Inicialização)"
    
    if 'service' in path_lower or 'controller' in path_lower or 'usecase' in path_lower:
        return "Lógica de Negócio / Controlador"
    
    if 'util' in path_lower or 'helper' in path_lower or 'common' in path_lower:
        return "Utilitário / Código Compartilhado"
    
    if 'model' in path_lower or 'schema' in path_lower or 'db' in path_lower or 'repository' in path_lower:
        return "Dados / Acesso a Banco"
    
    if 'ui' in path_lower or 'view' in path_lower or 'widget' in path_lower or 'theme' in path_lower:
        return "Interface de Usuário (UI/UX)"
    
    if 'test' in path_lower or 'spec' in path_lower:
        return "Testes"

    # Nova regra para documentação
    if filepath.endswith('.md') or filepath.endswith('.txt'):
        return "Documentação"

    return "Componente Padrão"

def extract_internal_imports_ast(filepath: str, project_files: list) -> list:
    """
    Lê a Árvore Sintática (AST) de um arquivo Python e descobre o que ele importa.
    Retorna apenas imports que fazem parte do projeto (ignora bibliotecas nativas como 'os', 'sys').
    """
    if not filepath.endswith('.py'):
        return []

    imported_modules = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.append(node.module)
    except Exception:
        # Se houver erro de sintaxe no arquivo, ignoramos silenciosamente
        return []

    # Extrai apenas os nomes base dos arquivos do projeto sem a extensão .py
    # Ex: /projeto/src/theme.py -> theme
    internal_modules = [os.path.splitext(os.path.basename(f))[0] for f in project_files if f.endswith('.py')]
    
    # Filtra: só queremos imports que batam com arquivos do nosso projeto
    project_dependencies = []
    for imp in imported_modules:
        base_imp = imp.split('.')[0] # pega a raiz do import, ex: 'widgets.StatCard' -> 'widgets'
        if base_imp in internal_modules:
            project_dependencies.append(imp)

    return list(set(project_dependencies))