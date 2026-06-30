// ─── Configuración ───────────────────────────────────────────────────────────

const CONFIG = {
  filas: 20,
  columnas: 20,
  zonas_esteriles: 80,
  tamano_celda: 22,
  margen_tablero: 8,
  panel_ancho: 180,
};

// Dimensiones del canvas
const CANVAS_W = CONFIG.panel_ancho + CONFIG.columnas * CONFIG.tamano_celda + CONFIG.margen_tablero * 2;
const CANVAS_H = CONFIG.filas * CONFIG.tamano_celda + CONFIG.margen_tablero * 2;

// Zona del tablero dentro del canvas
const TABLERO_X = CONFIG.panel_ancho + CONFIG.margen_tablero;
const TABLERO_Y = CONFIG.margen_tablero;

// ─── Estado del juego ────────────────────────────────────────────────────────

let tablero = [];
let estado_juego  = "jugando"; // "jugando" | "pausa" | "victoria" | "derrota"
let primera_jugada = true;
let celdas_reveladas = 0;
let marcas_puestas   = 0;

// NUEVO: guarda el estado antes de entrar en pausa
let estado_antes_pausa = null;

// ─── Temporizador ────────────────────────────────────────────────────────────

let segundos = 0;
let intervalo_tiempo = null;
let timestamp_ultimo_clic = null; // Para medir inactividad de Pebble

function iniciar_temporizador() {
  clearInterval(intervalo_tiempo);
  segundos = 0;
  intervalo_tiempo = setInterval(() => {
    if (estado_juego !== "jugando") return;
    segundos++;
    verificar_pebble_inactividad();
    dibujar_todo();
  }, 1000);
}

function detener_temporizador() {
  clearInterval(intervalo_tiempo);
}

// ─── Canvas ──────────────────────────────────────────────────────────────────

const canvas = document.getElementById("buscasemillas-canvas");
const ctx    = canvas.getContext("2d");

canvas.width  = CANVAS_W;
canvas.height = CANVAS_H;

// ─── Inicialización ──────────────────────────────────────────────────────────

function inicializar() {
  tablero = [];
  estado_juego    = "jugando";
  primera_jugada  = true;
  celdas_reveladas = 0;
  marcas_puestas   = 0;
  timestamp_ultimo_clic = null;
  pebble_activo   = false;
  estado_antes_pausa = null;  // Resetear

  for (let fila = 0; fila < CONFIG.filas; fila++) {
    tablero[fila] = [];
    for (let col = 0; col < CONFIG.columnas; col++) {
      tablero[fila][col] = {
        esteril:       false,
        revelada:      false,
        marcada:       false,
        vecinos:       0,
        brillo_pebble: false,
      };
    }
  }

  detener_temporizador();
  segundos = 0;
  dibujar_todo();
}

// ─── Generación ──────────────────────────────────────────────────────────────

function colocar_esteriles(fila_segura, col_segura) {
  let intentos = 0;

  do {
    // Limpiar estériles anteriores si estamos reintentando
    for (let fila = 0; fila < CONFIG.filas; fila++) {
      for (let col = 0; col < CONFIG.columnas; col++) {
        tablero[fila][col].esteril = false;
        tablero[fila][col].vecinos = 0;
      }
    }

    let colocadas = 0;
    while (colocadas < CONFIG.zonas_esteriles) {
      let fila = Math.floor(Math.random() * CONFIG.filas);
      let col  = Math.floor(Math.random() * CONFIG.columnas);
      if (fila === fila_segura && col === col_segura) continue;
      if (tablero[fila][col].esteril) continue;
      tablero[fila][col].esteril = true;
      colocadas++;
    }

    calcular_vecinos();
    intentos++;

    // Repetir hasta que la celda clickeada tenga vecinos === 0
  } while (tablero[fila_segura][col_segura].vecinos !== 0 && intentos < 100);
}

function calcular_vecinos() {
  for (let fila = 0; fila < CONFIG.filas; fila++) {
    for (let col = 0; col < CONFIG.columnas; col++) {
      if (tablero[fila][col].esteril) continue;
      let count = 0;
      for (let df = -1; df <= 1; df++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (df === 0 && dc === 0) continue;
          let nf = fila + df;
          let nc = col  + dc;
          if (nf >= 0 && nf < CONFIG.filas && nc >= 0 && nc < CONFIG.columnas && tablero[nf][nc].esteril) count++;
        }
      }
      tablero[fila][col].vecinos = count;
    }
  }
}

// ─── Lógica de revelado ──────────────────────────────────────────────────────

function revelar(fila, col) {
  let celda = tablero[fila][col];
  if (celda.revelada || celda.marcada) return;
  celda.revelada = true;
  celda.brillo_pebble = false;
  celdas_reveladas++;
  if (!celda.esteril && celda.vecinos === 0) {
    for (let df = -1; df <= 1; df++) {
      for (let dc = -1; dc <= 1; dc++) {
        if (df === 0 && dc === 0) continue;
        let nf = fila + df;
        let nc = col  + dc;
        if (nf >= 0 && nf < CONFIG.filas && nc >= 0 && nc < CONFIG.columnas && !tablero[nf][nc].revelada) {
          revelar(nf, nc);
        }
      }
    }
  }
}

function verificar_victoria() {
  return celdas_reveladas >= (CONFIG.filas * CONFIG.columnas - CONFIG.zonas_esteriles);
}

// ─── Pebble ──────────────────────────────────────────────────────────────────

let pebble_activo = false;

function verificar_pebble_inactividad() {
  if (primera_jugada || pebble_activo) return;
  if (timestamp_ultimo_clic === null) return;

  let ahora = Date.now();
  let segundos_inactivo = (ahora - timestamp_ultimo_clic) / 1000;

  if (segundos_inactivo >= 30) {
    pebble_dar_pista();
  }
}

function pebble_dar_pista() {
  let candidatas = [];
  for (let fila = 0; fila < CONFIG.filas; fila++) {
    for (let col = 0; col < CONFIG.columnas; col++) {
      let c = tablero[fila][col];
      if (!c.esteril && !c.revelada && !c.marcada) candidatas.push({ fila, col });
    }
  }
  if (candidatas.length === 0) return;

  let elegida = candidatas[Math.floor(Math.random() * candidatas.length)];
  tablero[elegida.fila][elegida.col].brillo_pebble = true;
  pebble_activo = true;

  // El brillo dura 2.5 segundos
  setTimeout(() => {
    if (tablero[elegida.fila]?.[elegida.col]) {
      tablero[elegida.fila][elegida.col].brillo_pebble = false;
    }
    pebble_activo = false;
    // Resetear el timestamp para que el contador de 30s arranque de nuevo
    timestamp_ultimo_clic = Date.now();
    dibujar_todo();
  }, 2500);
}

function pebble_corregir_marca(fila, col) {
  setTimeout(() => {
    let celda = tablero[fila]?.[col];
    if (!celda) return;
    if (celda.marcada && !celda.esteril && !celda.revelada) {
      celda.marcada = false;
      marcas_puestas--;
      dibujar_todo();
    }
  }, 4000);
}

// ─── Eventos ─────────────────────────────────────────────────────────────────

canvas.addEventListener("click", (e) => {
  let rect   = canvas.getBoundingClientRect();
  let escala_x = canvas.width  / rect.width;
  let escala_y = canvas.height / rect.height;
  let cx     = (e.clientX - rect.left) * escala_x;
  let cy     = (e.clientY - rect.top)  * escala_y;

  // El botón de pausa siempre responde
  // El botón de pausa siempre responde, sin importar el estado
  if (en_boton_pausa(cx, cy)) {
    if (estado_juego === "jugando") {
      estado_antes_pausa = "jugando";
      toggle_pausa();
    } else if (estado_juego === "pausa") {
      toggle_pausa();  // Esto restaurará el estado anterior (victoria/derrota o jugando)
    } else if (estado_juego === "victoria" || estado_juego === "derrota") {
      estado_antes_pausa = estado_juego;
      estado_juego = "pausa";
    }
    dibujar_todo();
    return;
  }

  // Botones del menú de pausa
  if (estado_juego === "pausa") {
    manejar_clic_pausa(cx, cy);
    return;
  }

  if (estado_juego !== "jugando") return;

  let col  = Math.floor((cx - TABLERO_X) / CONFIG.tamano_celda);
  let fila = Math.floor((cy - TABLERO_Y) / CONFIG.tamano_celda);
  if (fila < 0 || fila >= CONFIG.filas || col < 0 || col >= CONFIG.columnas) return;

  let celda = tablero[fila][col];
  if (celda.revelada || celda.marcada) return;

  if (primera_jugada) {
    colocar_esteriles(fila, col);
    primera_jugada = false;
    iniciar_temporizador();
  }

  timestamp_ultimo_clic = Date.now();

  if (celda.esteril) {
    celda.revelada = true;
    estado_juego   = "derrota";
    detener_temporizador();
    dibujar_todo();
    return;
  }

  revelar(fila, col);

  if (verificar_victoria()) {
    estado_juego = "victoria";
    detener_temporizador();
  }

  dibujar_todo();
});

canvas.addEventListener("contextmenu", (e) => {
  e.preventDefault();
  if (estado_juego !== "jugando") return;

  let rect   = canvas.getBoundingClientRect();
  let escala_x = canvas.width  / rect.width;
  let escala_y = canvas.height / rect.height;
  let cx     = (e.clientX - rect.left) * escala_x;
  let cy     = (e.clientY - rect.top)  * escala_y;

  let col  = Math.floor((cx - TABLERO_X) / CONFIG.tamano_celda);
  let fila = Math.floor((cy - TABLERO_Y) / CONFIG.tamano_celda);
  if (fila < 0 || fila >= CONFIG.filas || col < 0 || col >= CONFIG.columnas) return;

  let celda = tablero[fila][col];
  if (celda.revelada) return;

  timestamp_ultimo_clic = Date.now();

  if (celda.marcada) {
    celda.marcada = false;
    marcas_puestas--;
  } else {
    celda.marcada = true;
    marcas_puestas++;
    if (!celda.esteril) pebble_corregir_marca(fila, col);
  }

  dibujar_todo();
});

// ─── Pausa ───────────────────────────────────────────────────────────────────

// Posición y tamaño del botón de pausa (icono cuadrado arriba izquierda)
const PAUSA_BTN = { x: 14, y: 14, w: 36, h: 36, radio: 8 };

// Botones del menú de pausa (se generan dinámicamente según estado_antes_pausa)
function obtener_botones_pausa() {
  if (estado_antes_pausa === "jugando") {
    return [
      { label: "Continuar", accion: "continuar" },
      { label: "Reiniciar", accion: "reiniciar" },
      { label: "Menú",      accion: "menu" }
    ];
  } else {
    // Si se pausó desde victoria/derrota, no mostramos "Continuar"
    return [
      { label: "Reiniciar", accion: "reiniciar" },
      { label: "Menú",      accion: "menu" }
    ];
  }
}

function en_boton_pausa(cx, cy) {
  return cx >= PAUSA_BTN.x && cx <= PAUSA_BTN.x + PAUSA_BTN.w &&
         cy >= PAUSA_BTN.y && cy <= PAUSA_BTN.y + PAUSA_BTN.h;
}

function toggle_pausa() {
  if (estado_juego === "jugando") {
    estado_juego = "pausa";
    detener_temporizador();
    estado_antes_pausa = "jugando";
  } else if (estado_juego === "pausa") {
    if (estado_antes_pausa === "jugando") {
      estado_juego = "jugando";
      if (!primera_jugada) iniciar_temporizador();
    } else {
      // Restauramos el estado anterior (victoria o derrota)
      estado_juego = estado_antes_pausa;
      // No reiniciamos el temporizador
    }
    estado_antes_pausa = null;
  }
}

function manejar_clic_pausa(cx, cy) {
  let botones = obtener_botones_pausa();
  let menu_x  = 20;
  let menu_y  = 70;
  let btn_h   = 34;
  let btn_gap = 10;

  for (let i = 0; i < botones.length; i++) {
    let by = menu_y + i * (btn_h + btn_gap);
    if (cx >= menu_x && cx <= menu_x + 140 && cy >= by && cy <= by + btn_h) {
      let accion = botones[i].accion;
      if (accion === "continuar") {
        toggle_pausa();
      } else if (accion === "reiniciar") {
        inicializar();
      } else if (accion === "menu") {
        inicializar();  // Por ahora reinicia (podrías redirigir a un menú principal)
      }
      dibujar_todo();
      return;
    }
  }
}

// ─── Render — panel izquierdo ────────────────────────────────────────────────

function dibujar_panel() {
  // Fondo del panel
  ctx.fillStyle = "#2a3d1c";
  ctx.fillRect(0, 0, CONFIG.panel_ancho, CANVAS_H);

  // Línea separadora
  ctx.strokeStyle = "#4a6a2a";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(CONFIG.panel_ancho, 0);
  ctx.lineTo(CONFIG.panel_ancho, CANVAS_H);
  ctx.stroke();

  dibujar_boton_pausa();

  if (estado_juego === "pausa") {
    dibujar_menu_pausa();
  } else {
    dibujar_daffodil();
    dibujar_pebble();
    dibujar_hud();
  }
}

function dibujar_boton_pausa() {
  let { x, y, w, h, radio } = PAUSA_BTN;

  ctx.fillStyle = "#3d5c25";
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, radio);
  ctx.fill();

  ctx.strokeStyle = "#6a9a3a";
  ctx.lineWidth = 1;
  ctx.stroke();

  // Icono de pausa (dos barras verticales)
  ctx.fillStyle = "#c8e6a0";
  ctx.fillRect(x + 10, y + 10, 6, 16);
  ctx.fillRect(x + 20, y + 10, 6, 16);
}

function dibujar_menu_pausa() {
  ctx.fillStyle = "#c8e6a0";
  ctx.font      = "bold 13px monospace";
  ctx.textAlign = "center";
  ctx.fillText("— pausa —", CONFIG.panel_ancho / 2, 62);

  let botones = obtener_botones_pausa();
  let menu_x  = 20;
  let menu_y  = 75;
  let btn_w   = 140;
  let btn_h   = 34;
  let btn_gap = 10;

  for (let i = 0; i < botones.length; i++) {
    let by = menu_y + i * (btn_h + btn_gap);

    ctx.fillStyle = "#3d5c25";
    ctx.beginPath();
    ctx.roundRect(menu_x, by, btn_w, btn_h, 6);
    ctx.fill();

    ctx.strokeStyle = "#6a9a3a";
    ctx.lineWidth = 0.8;
    ctx.stroke();

    ctx.fillStyle = "#c8e6a0";
    ctx.font      = "13px monospace";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(botones[i].label, menu_x + btn_w / 2, by + btn_h / 2);
  }
}

function dibujar_daffodil() {
  // Zona central — placeholder hasta tener sprites
  let zona_y = 70;
  let zona_h = CANVAS_H - 70 - 90;

  ctx.strokeStyle = "#4a6a2a";
  ctx.lineWidth   = 0.8;
  ctx.setLineDash([4, 4]);
  ctx.strokeRect(14, zona_y, CONFIG.panel_ancho - 28, zona_h);
  ctx.setLineDash([]);

  ctx.fillStyle    = "#6a9a4a";
  ctx.font         = "11px monospace";
  ctx.textAlign    = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("Daffodil", CONFIG.panel_ancho / 2, zona_y + zona_h / 2 - 10);
  ctx.fillText("(animaciones)", CONFIG.panel_ancho / 2, zona_y + zona_h / 2 + 8);
}

function dibujar_pebble() {
  // Esquina inferior del área de Daffodil
  let zona_y = 70;
  let zona_h = CANVAS_H - 70 - 90;
  let px     = CONFIG.panel_ancho - 40;
  let py     = zona_y + zona_h - 30;

  ctx.fillStyle = "#b8f5a0";
  ctx.beginPath();
  ctx.arc(px, py, 12, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle    = "#2a3d1c";
  ctx.font         = "10px monospace";
  ctx.textAlign    = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("P", px, py);
}

function dibujar_hud() {
  let hud_y = CANVAS_H - 82;

  ctx.strokeStyle = "#4a6a2a";
  ctx.lineWidth   = 0.8;
  ctx.setLineDash([4, 4]);
  ctx.strokeRect(14, hud_y, CONFIG.panel_ancho - 28, 70);
  ctx.setLineDash([]);

  let marcas_restantes = CONFIG.zonas_esteriles - marcas_puestas;

  ctx.fillStyle    = "#c8e6a0";
  ctx.font         = "12px monospace";
  ctx.textAlign    = "left";
  ctx.textBaseline = "middle";
  ctx.fillText("⏱  " + segundos + "s",             24, hud_y + 20);
  ctx.fillText("⚑  " + marcas_restantes + " / " + CONFIG.zonas_esteriles, 24, hud_y + 44);
}

// ─── Render — tablero ────────────────────────────────────────────────────────

function dibujar_celda(fila, col) {
  let celda = tablero[fila][col];
  let x = TABLERO_X + col  * CONFIG.tamano_celda;
  let y = TABLERO_Y + fila * CONFIG.tamano_celda;
  let t = CONFIG.tamano_celda;

  if (!celda.revelada) {
    ctx.fillStyle = celda.brillo_pebble ? "#b8f5a0"
                  : celda.marcada       ? "#8B5E3C"
                  :                       "#5a7a3a";
    ctx.fillRect(x, y, t, t);
    ctx.strokeStyle = "#3d5c25";
    ctx.lineWidth   = 0.5;
    ctx.strokeRect(x, y, t, t);

    if (celda.marcada) {
      ctx.fillStyle    = "#f5e642";
      ctx.font         = "bold 12px monospace";
      ctx.textAlign    = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("⚑", x + t / 2, y + t / 2);
    }
    return;
  }

  if (celda.esteril) {
    ctx.fillStyle = estado_juego === "derrota" ? "#8B0000" : "#a0785a";
    ctx.fillRect(x, y, t, t);
    ctx.strokeStyle = "#6b4c35";
    ctx.lineWidth   = 0.5;
    ctx.strokeRect(x, y, t, t);
    ctx.fillStyle    = "#fff";
    ctx.font         = "bold 12px monospace";
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("✕", x + t / 2, y + t / 2);
    return;
  }

  // Fértil revelada
  ctx.fillStyle = "#c8e6a0";
  ctx.fillRect(x, y, t, t);
  ctx.strokeStyle = "#8aab5a";
  ctx.lineWidth   = 0.5;
  ctx.strokeRect(x, y, t, t);

  if (celda.vecinos > 0) {
    const colores = ["","#1a6b1a","#1a3e8b","#8b1a1a","#4b0082","#8b0000","#007b7b","#111","#555"];
    ctx.fillStyle    = colores[celda.vecinos];
    ctx.font         = "bold 11px monospace";
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(celda.vecinos, x + t / 2, y + t / 2);
  } else {
    ctx.fillStyle    = "#f9c74f";
    ctx.font         = "11px monospace";
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("✿", x + t / 2, y + t / 2);
  }
}

function dibujar_tablero_completo() {
  // Fondo del área del tablero
  ctx.fillStyle = "#1a2a0e";
  ctx.fillRect(CONFIG.panel_ancho, 0, CANVAS_W - CONFIG.panel_ancho, CANVAS_H);

  for (let fila = 0; fila < CONFIG.filas; fila++) {
    for (let col = 0; col < CONFIG.columnas; col++) {
      dibujar_celda(fila, col);
    }
  }

  // Overlay de victoria o derrota encima del tablero
  if (estado_juego === "victoria" || estado_juego === "derrota") {
    dibujar_overlay_tablero();
  }
}

function dibujar_overlay_tablero() {
  let tx = CONFIG.panel_ancho;
  let tw = CANVAS_W - CONFIG.panel_ancho;

  ctx.fillStyle = "rgba(0,0,0,0.6)";
  ctx.fillRect(tx, 0, tw, CANVAS_H);

  let mensaje = estado_juego === "victoria"
    ? "¡Campo cultivado! ✿"
    : "Tierra estéril...";
  let color = estado_juego === "victoria" ? "#c8e6a0" : "#e06060";

  ctx.fillStyle    = color;
  ctx.font         = "bold 16px monospace";
  ctx.textAlign    = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(mensaje, tx + tw / 2, CANVAS_H / 2 - 14);

  ctx.fillStyle = "#aaa";
  ctx.font      = "12px monospace";
  ctx.fillText("Usa Reiniciar para jugar de nuevo", tx + tw / 2, CANVAS_H / 2 + 12);
}

// ─── Render — principal ──────────────────────────────────────────────────────

function dibujar_todo() {
  ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
  dibujar_panel();
  dibujar_tablero_completo();
}

// ─── Arrancar ────────────────────────────────────────────────────────────────

inicializar();