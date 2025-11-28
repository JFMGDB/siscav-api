import cv2
import easyocr
import time
import csv
import os
import numpy as np
import warnings
import winsound

# Silencia avisos do EasyOCR
warnings.filterwarnings("ignore", category=UserWarning)

# =============== CONFIGURAÇÕES ==================
CAMERA_USB = 0
PASTA_PLACAS = "placas_detectadas"
ARQUIVO_CSV = "numeros.csv"
TEMPO_MAXIMO = 300  # segundos

os.makedirs(PASTA_PLACAS, exist_ok=True)
reader = easyocr.Reader(['en'], gpu=False)

# =============== FUNÇÕES ==================
def detectar_tipo_cor(placa_img):
    """Tenta identificar se a placa é branca (nova), amarela ou cinza (antiga)."""
    hsv = cv2.cvtColor(placa_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    media_v, media_h, media_s = np.mean(v), np.mean(h), np.mean(s)

    if media_s < 40 and media_v > 130:
        return "branca"
    elif 15 < media_h < 40 and media_s > 60:
        return "amarela"
    elif media_v < 120:
        return "cinza"
    else:
        return "desconhecida"


def preprocess_placa(placa_img, tipo="carro"):
    """Pré-processa imagem da placa para OCR (tons de cinza e contraste)."""
    cor = detectar_tipo_cor(placa_img)
    gray = cv2.cvtColor(placa_img, cv2.COLOR_BGR2GRAY)

    if cor in ["amarela", "cinza"]:
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        gray = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0), 3), -0.5, 0)
    else:
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

    if tipo == "moto":
        altura = 50
        largura = 7 * 20
        gray = cv2.resize(gray, (largura, altura), interpolation=cv2.INTER_CUBIC)
    else:
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    placa_bin = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    if np.sum(placa_bin == 0) > np.sum(placa_bin == 255):
        placa_bin = cv2.bitwise_not(placa_bin)

    return placa_bin, cor


def ler_placa(placa_img):
    resultado = reader.readtext(placa_img, detail=0, paragraph=True)
    if not resultado:
        return ""
    texto = "".join(resultado).replace(" ", "").upper()
    return "".join([c for c in texto if c.isalnum()])


def salvar_csv(texto, cor):
    existe = os.path.exists(ARQUIVO_CSV)
    with open(ARQUIVO_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["Placa", "Tipo", "DataHora"])
        writer.writerow([texto, cor, time.strftime("%Y-%m-%d %H:%M:%S")])


def salvar_imagem(placa_img, texto, cor):
    caminho = os.path.join(PASTA_PLACAS, f"{texto}{cor}{int(time.time())}.png")
    cv2.imwrite(caminho, placa_img)


# =============== CAPTURA DE CÂMERA ==================
cap = cv2.VideoCapture(CAMERA_USB)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("📸 Iniciando captura da câmera colorida...")
inicio = time.time()

# ================= LOOP PRINCIPAL =================
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Erro ao acessar a câmera.")
        break

    # Trabalha internamente com tons de cinza, mas exibe colorido
    gray_eq = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    edges = cv2.Canny(gray_eq, 100, 200)
    contornos, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)
        if w > 100 and h > 30:
            placa = frame[y:y + h, x:x + w]
            tipo = "carro" if w > h else "moto"

            placa_final, cor = preprocess_placa(placa, tipo)
            texto = ler_placa(placa_final)

            if len(texto) == 7:
                salvar_csv(texto, cor)
                salvar_imagem(placa_final, texto, cor)

                if tipo == "moto":
                    winsound.Beep(1000, 300)
                    print(f"🔊 Moto ({cor}) detectada: {texto}")
                else:
                    print(f"🚗 Carro ({cor}) detectado: {texto}")

                # Desenha retângulo colorido na imagem original
                cor_box = (0, 255, 0) if tipo == "carro" else (0, 255, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), cor_box, 2)
                cv2.putText(frame, texto, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_box, 2)

    cv2.imshow("Detecção de Placas - Câmera Colorida", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break
    if time.time() - inicio > TEMPO_MAXIMO:
        print("⏱ Tempo máximo atingido.")
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Finalizado.")