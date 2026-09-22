# Roteiro do vídeo InsurMinds

Duração planejada: aproximadamente 2 a 3 minutos. Arquivo: `InsurMinds_Projeto_Final.mp4`. O vídeo pode usar legendas explicativas em português e captura real da aplicação. Sem atribuir resultados simulados à IA.

## Versão demonstrativa incluída

1. Problema: apólices D&O reúnem limites, coberturas e exceções que precisam ser lidos em conjunto. A comparação manual exige localizar e conferir essas informações.
2. Solução: o InsurMinds organiza 16 critérios por documento e preserva o trecho e a página usados como evidência.
3. Arquitetura: React comunica-se com uma API Python. A leitura usa texto do PDF ou visão multimodal. A OpenAI estrutura dados, a validação confere evidências e o SQLite preserva o histórico.
4. Biblioteca: mostrar a interface e carregar dois exemplos fictícios. Explicar que os exemplos têm dados pré-preenchidos e não acionam IA.
5. Seleção: marcar D&O Essencial e D&O Ampliada. Abrir a comparação. Mostrar limite, franquia e coberturas.
6. Evidências: filtrar diferenças e abrir o limite de responsabilidade. Mostrar o trecho e a página do PDF.
7. Exportação: baixar o relatório PDF. Abrir o histórico para demonstrar persistência.
8. Upload: mostrar o recebimento de PDF ou imagem e explicar que uma chave no servidor habilita a extração real. Não apresentar a tela de configuração como processamento executado.
9. Resultados e limites: nos exemplos há 10 diferenças textuais em 16 critérios. Isso não representa avaliação de precisão de um modelo. A validação com IA real e documentos de mercado continua pendente.

## Complemento obrigatório antes da entrega ao I2A2

Configurar `OPENAI_API_KEY` em `.env`, reiniciar a API e regravar a demonstração incluindo um upload de PDF e um de imagem. Aguardar a extração, abrir evidências e comparar dois documentos processados pelo modelo. Citar o modelo usado e informar limitações observadas.

Identificar nominalmente os integrantes no README e no pitch. Revisar o relatório com a equipe e tornar público o repositório após a revisão do conteúdo. Prazo informado: 06/10/2026 às 23h59.
