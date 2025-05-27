import customtkinter as ctk
import os
from openai import OpenAI
from dotenv import load_dotenv
import threading
import pyautogui
import time

def get_pixel_color_at_mouse():
    x, y = pyautogui.position()
    screenshot = pyautogui.screenshot()
    color = screenshot.getpixel((x, y))
    return '#%02x%02x%02x' % color  # Retorna cor em HEX


# Carrega variáveis do .env
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

# Configuração do tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Cliente OpenAI
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

class GuruApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chromer")
        self.geometry("900x500")

        self.opacity = 1.0
        self.ctrl_o_active = False


        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        

        self.label = ctk.CTkLabel(self, text="TECH256", font=ctk.CTkFont(size=20, weight="bold"))
        # self.label.grid(row=0, column=0, pady=10)
        self.label.pack(padx=20, pady=20, fill="both", expand=True)

        # Chat exibido
        self.chatbox = ctk.CTkTextbox(self,height=100, wrap="word", font=("Consolas", 9))
        # self.chatbox.grid(row=1, column=0, sticky="ew", padx=20)
        self.chatbox.pack(pady=(0, 10), fill="both", expand=True)
        self.chatbox.configure(state="disabled")

        # Área de texto editável para compor mensagem
        self.input_textbox = ctk.CTkTextbox(self, height=100, font=("Consolas", 9))
        # self.input_textbox.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.input_textbox.pack(pady=(0, 10), fill="both", expand=True)



        self.send_button = ctk.CTkButton(self, text="Enviar", command=self.send_message)
        # self.send_button.grid(row=3, column=0, pady=(0, 20))
        self.send_button.pack()

        self.opacity_slider = ctk.CTkSlider(self.main_frame, from_=0.2, to=1.0, number_of_steps=14, command=self.mudar_opacidade)
        self.opacity_slider.set(1.0)
        self.opacity_slider.pack(pady=10)

        self.pick_button = ctk.CTkButton(self, text="Extrair cor do fundo", command=self.start_color_pick)
        self.pick_button.pack(pady=10)

        # Bind de teclado
        self.bind_all("<Control-o>", self.ctrl_o)
        self.bind_all("<KeyRelease-o>", self.ctrl_o_release)
        self.bind_all("<Key-plus>", self.aumentar_opacidade)
        self.bind_all("<Key-minus>", self.diminuir_opacidade)


        self.messages = [
            {
                "role": "system", 
                "content": "Você é um professor guru em tecnologia. Responda de forma clara e objetiva. seja direto, sem muitas explicações"
                }
        ]

    def append_message(self, sender, message):
        self.chatbox.configure(state="normal")
        self.chatbox.insert("end", f"{sender}: \n\n{message}\n\n")
        self.chatbox.configure(state="disabled")
        self.chatbox.see("end")

    def send_message(self):
        user_input = self.input_textbox.get("1.0", "end").strip()
        if not user_input:
            return

        self.append_message("Você", user_input)
        self.messages.append({"role": "user", "content": user_input})
        self.input_textbox.delete("1.0", "end")

        threading.Thread(target=self.get_response, daemon=True).start()

    def get_response(self):
        try:
            response = client.chat.completions.create(
                messages=self.messages,
                temperature=1.0,
                top_p=1.0,
                model=model
            )
            reply = response.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": reply})
            self.append_message("Professor Guru", reply)
        except Exception as e:
            self.append_message("Erro", f"Ocorreu um erro: {str(e)}")

    def mudar_opacidade(self, valor):
        self.opacity = float(valor)
        self.attributes("-alpha", self.opacity)

    def ctrl_o(self, event=None):
        self.ctrl_o_active = True

    def ctrl_o_release(self, event=None):
        self.ctrl_o_active = False

    def aumentar_opacidade(self, event=None):
        if self.ctrl_o_active and self.opacity < 1.0:
            self.opacity = min(self.opacity + 0.05, 1.0)
            self.opacity_slider.set(self.opacity)
            self.attributes("-alpha", self.opacity)

    def diminuir_opacidade(self, event=None):
        if self.ctrl_o_active and self.opacity > 0.3:
            self.opacity = max(self.opacity - 0.05, 1.0)
            self.opacity_slider.set(self.opacity)
            self.attributes("-alpha", self.opacity)
    

    def start_color_pick(self):
        self.withdraw()  # Esconde a janela para o usuário clicar atrás
        time.sleep(1)    # Dá tempo para o usuário escolher
        color = get_pixel_color_at_mouse()
        print("Cor detectada:", color)
        self.after(500, lambda: self.apply_color(color))

    def apply_color(self, hex_color):
        self.deiconify()  # Mostra a janela de novo
        self.configure(fg_color=hex_color)
# Rodar app
if __name__ == "__main__":
    app = GuruApp()
    app.mainloop()
