import os
import time
import queue
import sys
import gc
import smtplib
from email.message import EmailMessage

# Bibliotecas de Áudio e IA
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper
from pydub import AudioSegment
from groq import Groq
from fpdf import FPDF
from dotenv import load_dotenv

class Hackathon:
    def __init__(self):
        # 1. Configuracoes e Chaves
        load_dotenv()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        
        # 2. Parametros de Arquivos
        self.frequencia = 44200
        self.canais = 1
        self.arquivo_audio = "audio_projeto.wav"
        self.arquivo_texto = "resultado.md"
        # Lista com os dois PDFs: Professor e Aluno
        self.pdfs_gerados = ["relatorio_professor.pdf", "guia_aluno.pdf"]
        
        self.buffer_audio = queue.Queue()
        self.dados_totais = []

    def _enviar_email(self, destinatario, assunto, corpo, anexos):
        """Envia e-mail com múltiplos anexos (Professor e Aluno)."""
        msg = EmailMessage()
        msg['Subject'] = assunto
        msg['From'] = self.email_user
        msg['To'] = destinatario
        msg.set_content(corpo)
        
        for anexo in anexos:
            if os.path.exists(anexo):
                with open(anexo, 'rb') as f:
                    msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=anexo)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.email_user, self.email_pass)
            smtp.send_message(msg)
        print(f"E-mail enviado com sucesso para {destinatario}")

    def _salvar_pdf(self, texto, nome_arquivo, titulo):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, titulo, ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Helvetica", size=10)
        
        # Sanitização para evitar erros de caractere no FPDF
        texto_limpo = texto.replace("**", "").replace("#", "").replace("*", "-")
        texto_limpo = texto_limpo.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.multi_cell(0, 7, texto_limpo)
        pdf.output(nome_arquivo)

    def callback_audio(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.buffer_audio.put(indata.copy())

    def gravar_e_salvar(self):
        """Fase 1: Gravação (Para com CTRL+C)."""
        self.dados_totais = []
        print("\n--- STATUS: GRAVANDO ---")
        print("Pressione CTRL+C para gerar os relatorios do Professor e Aluno.")
        
        try:
            with sd.InputStream(samplerate=self.frequencia, channels=self.canais, callback=self.callback_audio):
                while True:
                    self.dados_totais.append(self.buffer_audio.get())
        except KeyboardInterrupt:
            print("\n--- GRAVACAO FINALIZADA ---")
            if self.dados_totais:
                audio_final = np.concatenate(self.dados_totais, axis=0)
                wav.write(self.arquivo_audio, self.frequencia, audio_final)
                print(f"Audio salvo: {self.arquivo_audio}")
                return True
        return False

    def transcrever_baixo_recurso(self):
        """Fase 2: Transcricao com Whisper."""
        print("\nSTATUS: TRANSCREVENDO...")
        modelo = whisper.load_model("small")
        audio = AudioSegment.from_wav(self.arquivo_audio)
        chunks = [audio[i:i + 600000] for i in range(0, len(audio), 600000)]
        
        texto_acumulado = []
        for i, chunk in enumerate(chunks):
            temp_file = f"temp_chunk_{i}.wav"
            chunk.export(temp_file, format="wav")
            res = modelo.transcribe(temp_file, language="pt", fp16=False)
            texto_acumulado.append(res["text"])
            os.remove(temp_file)
            gc.collect()

        with open(self.arquivo_texto, "w", encoding="utf-8") as f:
            f.write(" ".join(texto_acumulado))
        print("Transcricao concluida.")
        del modelo
        gc.collect()

    def processar_groq_e_enviar(self, email):
        """Fase 3: Analise Dupla via Groq e envio por e-mail."""
        print("\nSTATUS: ANALISANDO CONTEUDO PARA PROFESSOR E ALUNO...")
        if not os.path.exists(self.arquivo_texto):
            return

        with open(self.arquivo_texto, 'r', encoding='utf-8') as f:
            texto = f.read()

        # 1. Relatorio do Professor (Foco em didatica e pontos-chave)
        res_prof = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Aja como um consultor pedagogico. Gere um relatorio tecnico da aula para o PROFESSOR, destacando os temas abordados e sugestoes de melhoria: {texto[:10000]}"}]
        )
        conteudo_prof = res_prof.choices[0].message.content

        # 2. Guia do Aluno (Foco em resumo e exercicios)
        res_aluno = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Gere um guia de estudos para o ALUNO com um resumo simplificado da aula e 3 exercicios de fixacao sobre o tema: {texto[:10000]}"}]
        )
        conteudo_aluno = res_aluno.choices[0].message.content

        # Geracao dos PDFs
        self._salvar_pdf(conteudo_prof, self.pdfs_gerados[0], "Relatorio Pedagogico - Professor")
        self._salvar_pdf(conteudo_aluno, self.pdfs_gerados[1], "Guia de Estudos - Aluno")

        # Envio de e-mail com os dois anexos
        self._enviar_email(
            email, 
            "Material de Aula: Professor e Aluno", 
            "Ola, seguem em anexo os relatorios processados da aula.", 
            self.pdfs_gerados
        )

    def limpar_arquivos_finais(self):
        """Fase 4: Limpeza do Sistema."""
        print("\nSTATUS: LIMPANDO ARQUIVOS TEMPORARIOS...")
        arquivos = [self.arquivo_audio, self.arquivo_texto] + self.pdfs_gerados
        for f in arquivos:
            if os.path.exists(f):
                os.remove(f)
                print(f"Removido: {f}")

if __name__ == "__main__":
    app = Hackathon()
    try:
        if app.gravar_e_salvar():
            app.transcrever_baixo_recurso()
            # Envia para o seu e-mail os dois materiais
            app.processar_groq_e_enviar("matheusestebam123@gmail.com")
    finally:
        app.limpar_arquivos_finais()
    print("\nProcesso finalizado com sucesso.")