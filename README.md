# ClassInsight - Transcrição e Análise de Aulas - Hackathon IF

Este projeto automatiza o fluxo de captura de áudio, transcrição e geração de inteligência pedagógica. Ele foi desenvolvido com foco em **Eficiência de Processos Acadêmicos**, permitindo que uma aula gravada seja convertida em relatórios técnicos para professores e guias de estudo para alunos.

## 1. Ambiente de Testes e Validação em Hardware (Edge Computing)

Para comprovar a premissa de alta eficiência e baixo consumo de recursos, o sistema passou por testes de estresse em um ambiente controlado que reproduz as restrições de infraestrutura presentes em várias instituições de ensino.

### Detalhes da Unidade de Teste:
* **Hardware:** OrangePI RV2 .
* **Arquitetura:** RISC-V.
* **Memória RAM:** 4GB LPDDR4.
* **Sistema Operacional:** Ubuntu noble server linux 6.6.63.


## 2. Configuração do Ambiente (venv)

O projeto utiliza um Ambiente Virtual (venv) para isolar as dependências e garantir a portabilidade do software.

### Passos para instalação no Linux (Debion):

1. **Dependências do Sistema Operacional:**
   Abra o terminal e instale o FFmpeg (para processar áudio) e o PortAudio:
   ```bash
   sudo apt-get update
   sudo apt-get install ffmpeg libportaudio2 portaudio19-dev python3-pyaudio python3-venv -y
   
   ```
2. **Criação do Ambiente Virtual:** Na pasta raiz do projeto, execute:
  ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Instalação das Bibliotecas Python:** Com o  ```.venv ``` ativo, instale os pacotes necessários:
  ```bash
   pip install --upgrade pip
   pip install pyaudio speechrecognition sounddevice numpy scipy whisper-openai pydub groq fpdf2 python-dotenvv 
   ```
### Como Executar:

**Configuração de Credenciais**

Crie um arquivo ```.env``` na raiz do projeto com o seguinte conteúdo:
 ```bash
   GROQ_API_KEY=sua_chave_aqui
   EMAIL_USER=seu_email@gmail.com
   EMAIL_PASS=sua_senha_de_app_gmail
   ```
**Iniciando o Processo**
Execute o script principal:
 ```bash
 python main.py
   ```

## 3. Fluxo de Operação

O sistema foi arquitetado sob uma **pipeline sequencial e determinística**, otimizada para ambientes com restrições severas de hardware (dispositivos com 2GB de RAM).

### A. Módulo de Interrupção e Captura Multimodal
* **Acesso ao Hardware**: o sistema cria um fluxo de áudio por meio da interface `sounddevice`, funcionando com uma taxa de amostragem de **44.2kHz** em canal mono, assegurando precisão para a transcrição subsequente.
* **Concorrência por Multithreading**: Para reduzir o *overhead* do processador, a captura emprega uma **Thread dedicada** e uma estrutura de dados `queue.Queue`. Isso garante que a gravação não apresente *jitter* (atraso) durante o monitoramento simultâneo de comandos de voz pelo sistema.
* **Interrupção Híbrida**:
   * **Comando de Voz**: uma thread secundária usa a biblioteca `SpeechRecognition` para acompanhar a palavra-chave **"PARAR"** em tempo real. Quando o comando é identificado, o sistema indica o término da gravação por meio de um *flag* de sincronização.
   * **Sinal de Hardware**: Como uma medida de redundância, o sistema permite o encerramento por meio do **SIGINT (CTRL+C)**, assegurando que o buffer seja esvaziado (*flushed*) e que o descritor de arquivo `.wav` seja fechado de forma adequada.

### B. Módulo de Transcrição (Processamento de Sinais)
* **Segmentação Dinâmica (Chunking)**: Para funcionar dentro do limite de 2GB de RAM, o sistema divide o áudio em segmentos de 10 minutos (600.000ms) usando o `pydub`. Isso previne erros de *Out of Memory* (OOM) ao lidar com aulas longas.
* **Inferência Local**: Emprega o motor **OpenAI Whisper (Modelo Small)**. A decodificação fonética é executada localmente com o parâmetro `fp16=False`, assegurando compatibilidade e redução do uso de memória em CPUs que não possuem suporte ao ponto flutuante de meia precisão.
* **Gerenciamento de Memória**: Após transcrever cada segmento e ao término do módulo, o sistema realiza a liberação explícita do objeto do modelo e chama o `gc.collect()` para remover ponteiros de memória remanescentes.

### C. Módulo de Inteligência (Orquestração de Modelos de Linguagem)

Este módulo atua como o motor analítico do sistema, transformando dados brutos em conhecimento estruturado por meio de uma arquitetura de microsserviços em nuvem.

* **Otimização de Contexto e Payload**: o texto transcrito passa por um processo de filtragem e truncagem inteligente (com limite de 15.000 caracteres), assegurando que esteja em conformidade com a janela de contexto do modelo e prevenindo erros de *413 Payload Too Large*.
* **Gestão de Recursos Críticos (RAM)**: Antes de começar a orquestração da IA, o sistema realiza a liberação explícita do modelo Whisper da memória principal e chama o *Garbage Collector* (`gc.collect()`). Essa técnica é essencial para garantir a estabilidade do sistema em hardware com apenas 2GB de RAM, evitando problemas causados por *Memory Leak*.
* **Engenharia de Prompt Multidirecional**: Emprega o modelo de última geração **Llama 3.3 (70B)** para conduzir uma análise em dois âmbitos pedagógicos diferentes:
   * **Visão do Docente**: Concentrada na análise técnica, pedagógica e nas métricas de engajamento.
   * **Visão do Discente**: Concentrada na síntese de conteúdo e recursos para fixação (aprendizagem ativa).
* **Resiliência e Rate Limiting**: Adota um controle rigoroso de taxa para atender aos limites da API Groq (**12.000 TPM** / **100.000 TPD**). O sistema administra as cotas de requisição por meio de pausas estratégicas, assegurando a continuidade do serviço sem interrupções causadas por bloqueios de segurança do provedor.

### D. Módulo de Distribuição e Persistência Volátil
* **Renderização de Documentos**: Emprega a biblioteca `FPDF`. Para assegurar a integridade visual dos PDFs produzidos, o sistema utiliza uma camada de **sanitização e codificação Latin-1**, eliminando caracteres especiais do Markdown.
* **Segurança na Transmissão**: A transmissão ocorre por meio do protocolo **SMTP sobre SSL** utilizando a porta **465**. Isso assegura que as credenciais e os documentos acadêmicos sejam transmitidos de forma criptografada entre o sistema e os servidores de e-mail.
* **Idempotência e Cleanup**: O software emprega o bloco estrutural `finally` para garantir que, independentemente do êxito ou fracasso da execução, todos os arquivos temporários (`.wav`, `.md`, `.pdf`) sejam eliminados. Isso assegura a **idempotência do sistema**, mantendo o ambiente limpo para o próximo ciclo de uso.


## 4. Análise de Resultados e Impacto Pedagógico

A execução do ClassInsight gera dois artefatos diferentes, cujos conteúdos provêm de um processamento semântico profundo, assegurando uma aplicação prática imediata para o ecossistema acadêmico.

### A. O Relatório Pedagógico (Foco no Docente)
O resultado apresentado ao professor vai além de uma simples transcrição literal. O relatório fornece, por meio da análise analítica do modelo Llama 3.3:
* **Métricas de Estrutura:** Indicação precisa do tempo dedicado a cada assunto, possibilitando ao professor verificar a execução do plano de aula e a administração do tempo.
* **Diagnóstico de Engajamento:** A IA detecta padrões nas interações dos alunos, indicando os momentos de maior envolvimento ou possíveis períodos de dispersão, funcionando como um *feedback* retroativo da dinâmica da sala de aula.
* **Consultoria Didática:** O sistema propõe novas estratégias para conceitos que mostraram ser mais complexos na fala, incentivando a formação continuada fundamentada em evidências concretas da prática docente.

### B. O Guia de Estudos (Concentrado no Estudante)
Para o estudante, o sistema funciona como um assistente cognitivo que ajuda a reduzir a sobrecarga de informações:
* **Síntese Inteligente:** Conversão de discursos repetitivos ou informais em conceitos técnicos claros e estruturados.
* **Material de Revisão Personalizado:** O resumo produzido espelha precisamente o que foi abordado em sala de aula, estabelecendo uma conexão entre a apresentação oral e o material impresso.
* **Avaliação Formativa:** Os exercícios de fixação são criados a partir dos exemplos práticos mencionados em sala de aula, fortalecendo a ligação entre a teoria apresentada e sua aplicação prática.




