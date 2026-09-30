import React, { useState, useRef } from "react";
import {
  SafeAreaView, View, Text, TextInput, TouchableOpacity, FlatList,
  Switch, StyleSheet, ActivityIndicator, Image, KeyboardAvoidingView, Platform,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as Speech from "expo-speech";
import { askCloud } from "./cloud";
import { loadLocalModel, askLocal } from "./local";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [image, setImage] = useState(null); // { uri, base64 }
  const [local, setLocal] = useState(false);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [speak, setSpeak] = useState(false);
  const list = useRef(null);

  const toggleLocal = async (on) => {
    setLocal(on);
    if (!on) return;
    try {
      setBusy(true);
      setStatus("Preparando modelo local…");
      await loadLocalModel((p) => setStatus(`Descargando modelo… ${Math.round(p * 100)}%`));
      setStatus("");
    } catch (e) {
      setLocal(false);
      setStatus("No se pudo cargar el modelo local: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const pickImage = async () => {
    const r = await ImagePicker.launchImageLibraryAsync({ base64: true, quality: 0.5 });
    if (!r.canceled) setImage({ uri: r.assets[0].uri, base64: r.assets[0].base64 });
  };

  const send = async () => {
    const text = input.trim();
    if ((!text && !image) || busy) return;
    const next = [...messages, { role: "user", content: text, uri: image?.uri }];
    setMessages(next);
    setInput("");
    const img = image?.base64;
    setImage(null);
    setBusy(true);
    try {
      const plain = next.map(({ role, content }) => ({ role, content }));
      const reply = local ? await askLocal(plain) : await askCloud(plain, img);
      setMessages([...next, { role: "assistant", content: reply }]);
      if (speak) Speech.speak(reply, { language: "es-ES" });
    } catch (e) {
      setMessages([...next, { role: "assistant", content: "Error: " + e.message }]);
    } finally {
      setBusy(false);
      setTimeout(() => list.current?.scrollToEnd(), 100);
    }
  };

  return (
    <SafeAreaView style={s.root}>
      <View style={s.bar}>
        <Text style={s.title}>Asistente IA</Text>
        <View style={s.row}>
          <Text>Local</Text>
          <Switch value={local} onValueChange={toggleLocal} disabled={busy} />
          <Text> Voz</Text>
          <Switch value={speak} onValueChange={setSpeak} />
        </View>
      </View>
      {!!status && <Text style={s.status}>{status}</Text>}
      <FlatList
        ref={list}
        data={messages}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <View style={[s.bubble, item.role === "user" ? s.user : s.bot]}>
            {item.uri && <Image source={{ uri: item.uri }} style={s.img} />}
            <Text style={item.role === "user" ? s.userText : undefined}>{item.content}</Text>
          </View>
        )}
      />
      {busy && <ActivityIndicator style={{ margin: 8 }} />}
      {image && <Image source={{ uri: image.uri }} style={s.preview} />}
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <View style={s.inputRow}>
          <TouchableOpacity onPress={pickImage} disabled={local}>
            <Text style={[s.icon, local && { opacity: 0.3 }]}>📷</Text>
          </TouchableOpacity>
          <TextInput
            style={s.input}
            value={input}
            onChangeText={setInput}
            placeholder="Escriba un mensaje…"
            onSubmitEditing={send}
            multiline
          />
          <TouchableOpacity onPress={send} disabled={busy}>
            <Text style={s.icon}>➤</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#fff" },
  bar: { padding: 12, borderBottomWidth: 1, borderColor: "#eee" },
  row: { flexDirection: "row", alignItems: "center", marginTop: 4 },
  title: { fontSize: 18, fontWeight: "600" },
  status: { padding: 8, color: "#666" },
  bubble: { maxWidth: "85%", padding: 10, borderRadius: 12, marginBottom: 8 },
  user: { alignSelf: "flex-end", backgroundColor: "#2563eb" },
  userText: { color: "#fff" },
  bot: { alignSelf: "flex-start", backgroundColor: "#f1f5f9" },
  img: { width: 160, height: 160, borderRadius: 8, marginBottom: 6 },
  preview: { width: 64, height: 64, margin: 8, borderRadius: 8 },
  inputRow: { flexDirection: "row", alignItems: "center", padding: 8, borderTopWidth: 1, borderColor: "#eee" },
  input: { flex: 1, borderWidth: 1, borderColor: "#ddd", borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, marginHorizontal: 8, maxHeight: 100 },
  icon: { fontSize: 24 },
});
