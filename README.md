# CodeGrimoire

## Descrição
O CodeGrimoire é uma ferramenta projetada para automatizar a consolidação de arquivos de código-fonte em documentos Markdown estruturados. O objetivo é facilitar a leitura, a documentação e, principalmente, a análise técnica de projetos de software complexos.

## Proposta
O programa nasceu da necessidade de unir grandes quantidades de código de forma organizada para análise. Em cenários onde é preciso fornecer contexto completo de um projeto para revisores humanos ou modelos de linguagem de larga escala (LLMs), a coleta manual de arquivos é ineficiente. O CodeGrimoire automatiza essa tarefa, permitindo que o usuário selecione arquivos específicos, preserve a hierarquia de diretórios e gere um arquivo final formatado com realce de sintaxe.

## Estado do Projeto
Este projeto encontra-se em um estado inicial de desenvolvimento. Por ser uma ferramenta nova, o código foi pouco testado em diferentes ambientes e estruturas de pastas variadas. O usuário deve estar ciente de que o software está em estágio experimental e pode apresentar instabilidades ou comportamentos inesperados.

## Funcionalidades Atuais
* Exploração visual de diretórios com seleção via checkbox.
* Filtros personalizáveis para ignorar pastas e arquivos específicos (ex: node_modules, .git).
* Geração de Markdown detalhado, incluindo estrutura de pastas e sumário.
* Otimização de conteúdo através da remoção de comentários e minificação de espaços em branco.
* Divisão automática do resultado em múltiplas partes quando o volume de código excede limites operacionais.
* Sistema de presets para salvar e carregar seleções de arquivos frequentes.
* Interface gráfica intuitiva com suporte a temas e logs em tempo real.

## Requisitos de Sistema
* Python 3.9 ou superior.
* PySide6 (interface gráfica).

## Instalação e Execução
1. Instale as dependências necessárias:
   `pip install PySide6`
2. Execute o programa:
   `python main.py`

## Autor
**Matheus Araújo**
Estudante de Ciência da Computação
Universidade Estadual do Piauí (UESPI) - Campus Parnaíba

## Licença
Este projeto é distribuído para fins de estudo e uso pessoal. Como se trata de um projeto em estágio inicial, contribuições e relatos de problemas são bem-vindos para o aprimoramento da ferramenta.