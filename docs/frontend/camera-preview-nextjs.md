# Pré-visualização de câmara (USB e Wi‑Fi) — Next.js + TypeScript

Guia de implementação para o **repositório frontend** (Next.js, TypeScript). A API SISCAV neste monorepo **não** serve o stream de vídeo no MVP descrito em `.planning/.../999.1-CONTEXT.md`; o tráfego de preview é sobretudo **browser ↔ câmara** ou **browser ↔ URL do equipamento**.

## Objetivo

- **USB:** ligar uma câmara USB ao posto do operador e mostrar **vídeo em tempo real** no browser.
- **Wi‑Fi / rede:** configurar uma **URL** (câmara IP ou serviço compatível) e mostrar **preview contínuo** quando o formato for suportado pelo browser ou por biblioteca auxiliar.

### Fora de âmbito deste guia

- OCR / leitura automática de matrícula na página.
- Envio de frame para `POST /api/v1/access_logs/` (multipart) — a API já suporta; integração “capturar → enviar” é trabalho separado.
- Gravação longa, DVR, WebRTC com TURN, proxy de vídeo na FastAPI.

## Pré-requisitos

- Node.js 18+ e projeto **Next.js** com **TypeScript**.
- Em **produção**, o site deve servir-se por **HTTPS** (ou `localhost` em dev) para `navigator.mediaDevices.getUserMedia` funcionar de forma previsível.
- Variável de ambiente pública sugerida para chamadas REST à SISCAV:

  `NEXT_PUBLIC_SISCAV_API_URL=http://127.0.0.1:8000`

  (Ajustar host/porta ao ambiente; não usar este valor para o stream MJPEG da câmara IP.)

## Arquitetura (visão geral)

```
Operador (browser)
    │
    ├─► USB: getUserMedia → MediaStream → <video>
    │
    ├─► Wi‑Fi: URL (MJPEG / HLS / snapshots) → <img> ou <video> (+ hls.js se preciso)
    │
    └─► API SISCAV: fetch com Authorization Bearer (login, whitelist, etc.)
            ↑ apenas quando precisar de dados da API; o preview não exige JWT
```

A API em `NEXT_PUBLIC_SISCAV_API_URL` trata de JWT conforme [`FRONTEND_INTEGRATION.md`](../api/FRONTEND_INTEGRATION.md). O **preview** em si não precisa de token.

## USB — getUserMedia e `<video>`

### Client Component

Em **App Router**, qualquer uso de `navigator`, `document` ou hooks que toquem no DOM do browser deve estar em ficheiro com **`'use client'`** no topo (Client Component). Não colocar `getUserMedia` em Server Components.

### Fluxo recomendado

1. Utilizador escolhe **“Câmara USB”** (ou equivalente).
2. Chamar `navigator.mediaDevices.getUserMedia({ video: true })` (ou `video: { deviceId: { exact: id } }` após listar dispositivos).
3. Atribuir o stream a um `<video>`:

   ```tsx
   videoRef.current.srcObject = stream;
   await videoRef.current.play();
   ```

4. Atributos úteis no `<video>`: `autoPlay`, `playsInline`, `muted` (muitos browsers exigem muted para autoplay).
5. **Cleanup** ao desmontar ou trocar de fonte:

   ```ts
   stream.getTracks().forEach((t) => t.stop());
   if (videoRef.current) videoRef.current.srcObject = null;
   ```

### Múltiplas câmaras

Após permissão inicial, `navigator.mediaDevices.enumerateDevices()` lista entradas `videoinput` com `deviceId`. Popular um `<select>` e passar o `deviceId` escolhido em `getUserMedia`.

### React Strict Mode (dev)

Em desenvolvimento o React 18 pode montar o componente duas vezes; garantir que `stop()` é idempotente e que não ficas com streams órfãos.

## Wi‑Fi / URL na rede

### MJPEG (multipart)

Muitas câmaras IP expõem um endpoint que devolve **MJPEG** contínuo. Tipicamente funciona bem com:

```tsx
<img src={cameraUrl} alt="Preview" />
```

Atualizações são contínuas sem `fetch` manual. **Cuidado:** conteúdo misto — página **HTTPS** não deve pedir stream **HTTP** (bloqueado pelo browser).

### HLS (m3u8)

Safari reproduz HLS nativamente em `<video src="...m3u8" />`. Em Chrome/Firefox costuma ser necessário **hls.js**: ligar o stream ao elemento `<video>` via biblioteca. Escolha da biblioteca fica a critério do projeto (ver `package.json` do repo Next).

### Snapshot polling

Se a câmara só expõe JPEG estático, podes fazer `fetch` periódico e atualizar `src` com object URL ou data URL. Simples mas mais carga na rede e CPU.

### CORS e rede

Se a câmara não envia cabeçalhos CORS e usas `fetch`, pode falhar. `<img>` para MJPEG costuma ser mais tolerante para **visualização**. Se no futuro precisares de proxy, isso é uma **fase separada** (não exigido no MVP da API SISCAV).

## UX sugerida (dois caminhos)

1. **Separador ou botão “USB / Este dispositivo”** — pede permissão, mostra preview no `<video>`, mensagem clara se o utilizador negar.
2. **Separador “Câmara na rede (URL)”** — campo de texto para URL, botão **Testar** / **Ligar**, preview em `<img>` ou `<video>` conforme o tipo.

Estados a mostrar texto ou spinner:

- Sem permissão / a aguardar utilizador.
- A carregar stream.
- Erro (rede, mixed content, URL inválida).
- Stream ativo.

## Segurança

- Não registar em logs URLs com **user:password** embutidos.
- Validar/formatar URL antes de passar ao DOM (evitar `javascript:`).
- Tokens JWT: armazenamento e refresh conforme [`FRONTEND_INTEGRATION.md`](../api/FRONTEND_INTEGRATION.md); não enviar secret da câmara para a API SISCAV se não for necessário.

## CORS com a API SISCAV

O backend em `apps/api/src/main.py` inclui `http://localhost:3000` e `http://127.0.0.1:3000` em `allow_origins` para desenvolvimento Next.js. Em produção, configurar origens reais se alterares o middleware CORS.

## Checklist de implementação (repo Next.js)

1. Criar rota ou página dedicada (ex. `/camera` ou secção no dashboard).
2. Componente **client** com `'use client'` para preview USB e URL.
3. Implementar fluxo USB: `getUserMedia` + `<video>` + cleanup.
4. Implementar fluxo URL: `<img>` para MJPEG OU `<video>` + hls.js para HLS.
5. Estados de UI: erro, carregamento, sucesso.
6. Definir `NEXT_PUBLIC_SISCAV_API_URL` no `.env.local`.
7. Testar em **Chrome desktop** (USB + URL se disponível).
8. Verificar **HTTPS** ou localhost antes de testar USB em staging.
9. Documentar no README do frontend limitações conhecidas (Safari iOS, mixed content).
10. Ver secção abaixo: **deteção de placa + `POST /api/v1/access_logs/`**.

## Deteção de placa e chamada à API

A **SISCAV API não executa OCR** nem devolve “placa encontrada” a partir da imagem. O contrato atual é:

- **`POST /api/v1/access_logs/`** — `multipart/form-data` com:
  - **`plate`** (string): texto da placa **já lido** (normalmente por OCR no cliente, câmara inteligente, ou entrada manual).
  - **`file`**: ficheiro de imagem (JPEG/PNG/WebP, conforme validação do servidor).

O servidor **normaliza** a placa, **compara com a whitelist** e grava o log com `Authorized` / `Denied` + caminho da imagem. Ou seja: **a interface (ou um serviço atrás dela) tem de produzir o texto da placa** antes do `POST`.

### Fluxo recomendado no Next.js

1. **Capturar um frame** do `<video>` (ou do stream MJPEG via canvas oculto): `drawImage` → `canvas.toBlob('image/jpeg')`.
2. **Obter o texto da placa** por um destes caminhos:
   - **OCR no browser** — ex.: [Tesseract.js](https://github.com/naptha/tesseract.js) no frame recortado (ROI da zona da placa melhora muito a taxa de acerto).
   - **Serviço externo** — Vision API / ALPR SaaS chamado do **servidor** Next.js (Route Handler) para não expor chaves no bundle.
   - **Manual** — operador confirma/edita a string antes de enviar.
3. **Validar formato** BR (Mercosul / antiga) no cliente se quiseres feedback rápido (a API também valida/normaliza).
4. **Enviar** com `fetch` + `FormData`:

```ts
const form = new FormData();
form.append("plate", plateString.trim());
form.append("file", imageBlob, "frame.jpg");

const headers: HeadersInit = {};
// Se DEVICE_INGEST_KEY estiver definido no servidor API, em produção precisas disto:
headers["X-Device-Key"] = deviceKey;

await fetch(`${process.env.NEXT_PUBLIC_SISCAV_API_URL}/api/v1/access_logs/`, {
  method: "POST",
  headers,
  body: form,
  // Não definir Content-Type — o browser define boundary do multipart
});
```

### Autenticação deste endpoint (`X-Device-Key`)

A rota de ingestão usa **`verify_device_ingest_key`**, não JWT:

- Se **`DEVICE_INGEST_KEY`** está definida no servidor da API → o pedido **deve** incluir cabeçalho **`X-Device-Key`** com o mesmo valor.
- Se **não** está definida e o ambiente é `development` / `dev` / vazio → o servidor pode aceitar sem chave (apenas para dev).

**Cuidado:** colocar a chave em `NEXT_PUBLIC_*` expõe a chave a **qualquer utilizador** que abra o DevTools. Para produção, o padrão mais seguro é:

- Um **Route Handler** ou **Server Action** no Next.js que recebe o `FormData`, adiciona `X-Device-Key` **só no servidor** (variável sem `NEXT_PUBLIC`) e faz o `fetch` à SISCAV; ou
- Uma extensão futura da API: ingestão autenticada com **JWT** de operador (ainda não existe neste repositório).

### “Quando há placas” — gatilhos na UI

- **Por intervalo:** `setInterval` a cada N segundos captura frame → OCR → se texto novo/confiante → `POST` (com debounce para não spammar a API).
- **Por botão:** “Registar passagem” captura frame atual + OCR uma vez.
- **Por movimento (avançado):** deteção de movimento no canvas antes de OCR para reduzir custo (fora do âmbito deste guia).

Trata sempre erros **401** (chave em falta/errada), **413** (imagem grande), **422** (validação) conforme mensagens da API.

## Referências cruzadas

- Contexto de produto e decisões: `.planning/phases/999.1-ui-camera-wifi-usb-live-preview/999.1-CONTEXT.md` (neste repositório da API).
- Pesquisa técnica: `999.1-RESEARCH.md` na mesma pasta de fase.
- MDN: [getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia), [MediaStream](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream).
