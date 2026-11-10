"use strict";

const $ = (id) => document.getElementById(id);

const el = {
  form: $("note-form"),
  title: $("title"),
  content: $("content"),
  save: $("save"),
  message: $("message"),
  notes: $("notes"),
  empty: $("empty"),
  status: $("status"),
};

/*Mensajes y estado*/

function showMessage(text, type) {
  el.message.textContent = text;
  el.message.dataset.type = type;
}

async function checkStatus() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("sin conexión");
    const data = await response.json();
    el.status.dataset.type = "ok";
    el.status.textContent = `Conectado a la base de datos (${data.database})`;
  } catch (e) {
    el.status.dataset.type = "error";
    el.status.textContent = "Sin conexión con la base de datos";
  }
}

/*Notas*/

function createNoteItem(note) {
  const item = document.createElement("li");
  item.className = "note";

  const title = document.createElement("h3");
  title.textContent = note.title;

  const content = document.createElement("p");
  content.textContent = note.content;

  const date = document.createElement("time");
  date.textContent = note.created_at.slice(0, 16);

  const remove = document.createElement("button");
  remove.type = "button";
  remove.textContent = "Eliminar";
  remove.setAttribute("aria-label", `Eliminar la nota ${note.title}`);
  remove.addEventListener("click", () => deleteNote(note.id));

  item.append(title, content, date, remove);
  return item;
}

async function loadNotes() {
  try {
    const response = await fetch("/notes");
    if (!response.ok) throw new Error("error al leer");
    const notes = await response.json();

    el.notes.replaceChildren(...notes.map(createNoteItem));
    el.empty.hidden = notes.length > 0;
  } catch (e) {
    el.notes.replaceChildren();
    el.empty.hidden = true;
    showMessage("No se pudieron cargar las notas. Revisa la conexión con la base de datos.", "error");
  }
}

async function saveNote(event) {
  event.preventDefault();
  showMessage("", "");

  const title = el.title.value.trim();
  if (!title) {
    showMessage("Escribe un título para guardar la nota.", "error");
    el.title.focus();
    return;
  }

  el.save.disabled = true;
  try {
    const response = await fetch("/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content: el.content.value }),
    });
    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "No se pudo guardar la nota.", "error");
      return;
    }

    el.form.reset();
    el.title.focus();
    await loadNotes();
    showMessage("Nota guardada.", "ok");
  } catch (e) {
    showMessage("No se pudo guardar. Revisa la conexión con la base de datos.", "error");
  } finally {
    el.save.disabled = false;
  }
}

async function deleteNote(id) {
  try {
    const response = await fetch(`/notes/${id}`, { method: "DELETE" });
    if (!response.ok && response.status !== 404) throw new Error("error al eliminar");
    await loadNotes();
    showMessage("Nota eliminada.", "ok");
  } catch (e) {
    showMessage("No se pudo eliminar la nota.", "error");
  }
}

/*Inicio*/

el.form.addEventListener("submit", saveNote);

checkStatus();
loadNotes();
setInterval(checkStatus, 10000);
