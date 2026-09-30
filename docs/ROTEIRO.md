# Roteiro para a gravação do vídeo InsurMinds

Duração sugerida: 2 a 3 minutos. A gravação ficará a cargo da equipe e deve mostrar a aplicação em execução. Identifique claramente quando usar exemplos fictícios; não apresente dados simulados como resultado do Gemini.

## Sequência sugerida

1. **Problema:** apólices D&O reúnem limites, coberturas e exceções que precisam ser lidos em conjunto. A comparação manual exige localizar e conferir essas informações.
2. **Solução:** o InsurMinds organiza 16 critérios por documento e mantém o trecho e a página usados como evidência.
3. **Arquitetura:** a interface React usa uma API Python. A leitura aproveita o texto do PDF ou envia imagens ao Gemini. O backend valida os dados e mantém o histórico no SQLite.
4. **Interface:** mostre a visão geral e explique que os exemplos Aurora e Vértice são fictícios e já vêm preenchidos; carregá-los não aciona IA.
5. **Comparação:** selecione os exemplos, abra a comparação e mostre limite, franquia, coberturas e filtro de diferenças.
6. **Evidências:** abra um critério e mostre seu trecho de origem e a página correspondente.
7. **Exportação e histórico:** gere o relatório PDF e retome a comparação pelo histórico.
8. **Análise com IA:** depois de configurar a chave Gemini no servidor, envie um documento de teste e mostre o processamento real. Diga qual modelo foi usado e identifique qualquer dado fictício que apareça na demonstração.
9. **Resultados e limites:** nos exemplos atuais há 10 diferenças textuais entre 16 critérios. Esse resultado demonstra a comparação dos dados pré-preenchidos; não mede a precisão do Gemini.

## Antes de gravar

A equipe testou o fluxo com o Gemini usando os PDFs fictícios do projeto. Na gravação, identifique esses documentos como material sintético e não sugira que o teste comprova a precisão em apólices de mercado. O vídeo anterior foi removido; salve a nova gravação como `Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4` quando estiver pronta.

Equipe InsurMinds: Victor Hugo Araujo, João Carlos Mendonça, Adriéli Zacharias e Bruno Veiga. Repositório público: https://github.com/vicTmm/i2a2-desafio-final. Prazo informado: 06/10/2026 às 23h59.
