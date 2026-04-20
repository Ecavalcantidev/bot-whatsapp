import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Base de conhecimento do bot
CARDAPIO = """
*Cardápio:*
1. Pizza G - R$45
2. Hambúrguer - R$25
3. Açaí 500ml - R$18
Digite o número pra pedir
"""

PIX = "Chave PIX: ecavalcanti2017@gmail.com\nNome: Emerson Cavalcanti"
HORARIO = "Funcionamos de Seg a Sáb, das 18h às 23h"
ENDERECO = "Rua das Flores, 123 - Massapê, CE"

@app.route("/")
def home():
    return "Bot profissional online"

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.values.get('Body', '').strip()
    msg_lower = msg.lower()
    resp = MessagingResponse()

    # 1. COMANDOS
    if msg_lower == "!cardapio" or msg_lower == "cardapio":
        resp.message(CARDAPIO)
    elif msg_lower == "!preco" or msg_lower == "preco":
        resp.message(CARDAPIO)
    elif msg_lower == "!pix" or msg_lower == "pix":
        resp.message(PIX)
    elif msg_lower == "!horario" or msg_lower == "horario":
        resp.message(f"{HORARIO}\n{ENDERECO}")

    # 2. VENDAS - Pedido simples
    elif msg_lower in ["1", "2", "3"]:
        pedidos = {"1": "Pizza G - R$45", "2": "Hambúrguer - R$25", "3": "Açaí 500ml - R$18"}
        resp.message(f"Pedido: {pedidos[msg_lower]}\nPra finalizar, faça o PIX:\n{PIX}\n\nMe manda o comprovante aqui depois.")

    # 3. ATENDIMENTO AUTOMÁTICO
    elif "horario" in msg_lower or "abre" in msg_lower:
        resp.message(HORARIO)
    elif "endereco" in msg_lower or "local" in msg_lower:
        resp.message(ENDERECO)
    elif "oi" in msg_lower or "ola" in msg_lower:
        resp.message("Olá! Sou o assistente virtual 🤖\n\nDigite:\n*!cardapio* - Ver produtos\n*!pix* - Dados pra pagamento\n*!horario* - Funcionamento\n\nOu me faça uma pergunta que eu respondo com IA.")

    # 4. CHATGPT PRA TUDO RESTO
    else:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um atendente de WhatsApp de uma lanchonete em Massapê-CE. Seja breve, simpático e use emojis. Se perguntarem sobre pedidos, mande digitar!cardapio."},
                    {"role": "user", "content": msg}
                ]
            )
            resposta = completion.choices[0].message.content
            resp.message(resposta)
        except Exception as e:
            print(f"ERRO OPENAI: {e}")
            resp.message("Não consegui falar com a IA agora. Digite!cardapio pra ver os produtos.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
