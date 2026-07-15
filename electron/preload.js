// Puente mínimo y aislado entre el launcher (React) y el proceso principal.
// Solo expone: escuchar el estado del arranque y pedir un reintento.
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("mvdg", {
  onStatus: (cb) => ipcRenderer.on("mvdg:status", (_ev, data) => cb(data)),
  retry: () => ipcRenderer.invoke("mvdg:retry"),
});
