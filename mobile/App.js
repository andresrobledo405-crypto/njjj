import React, { useState, useRef, useEffect, useMemo } from "react";
import {
  SafeAreaView, View, Text, TextInput, Pressable, FlatList, Switch, StyleSheet,
  Image, KeyboardAvoidingView, Platform, Animated, Easing, AccessibilityInfo, useColorScheme,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as Speech from "expo-speech";
import { askCloud } from "./cloud";
import { loadLocalModel, askLocal } from "./local";
import { palette } from "./theme";
import Deals from "./Deals";

// Strong ease-out for entering elements (Emil Kowalski): fast start, soft landing.
const EASE_OUT = Easing.bezier(0.23, 1, 0.32, 1);

// Reduced motion is respected everywhere: durations collapse to 0 (opacity-only intent is kept by the final state).
function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduced);
    const sub = AccessibilityInfo.addEventListener("reduceMotionChanged", setReduced);
    return () => sub.remove();
  }, []);
  return reduced;
}

// New message: opacity + 8px rise, 220ms. Occasional event, so a standard animation is earned.
function Enter({ reduced, children, style }) {
  const v = useRef(new Animated.Value(reduced ? 1 : 0)).current;
  useEffect(() => {
    if (reduced) return;
    Animated.timing(v, { toValue: 1, duration: 220, easing: EASE_OUT, useNativeDriver: true }).start();
  }, []);
  return (
    <Animated.View style={[style, { opacity: v, transform: [{ translateY: v.interpolate({ inputRange: [0, 1], outputRange: [8, 0] }) }] }]}>
      {children}
    </Animated.View>
  );
}

// Press feedback: scale(0.96) in 100ms, back on release. Never from scale(0).
function PressScale({ onPress, disabled, style, children, label, reduced }) {
  const v = useRef(new Animated.Value(1)).current;
  const to = (x) => !reduced && Animated.timing(v, { toValue: x, duration: 100, easing: EASE_OUT, useNativeDriver: true }).start();
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      onPressIn={() => to(0.96)}
      onPressOut={() => to(1)}
      accessibilityRole="button"
      accessibilityLabel={label}
      hitSlop={6}
    >
      <Animated.View style={[style, { transform: [{ scale: v }] }, disabled && { opacity: 0.4 }]}>{children}</Animated.View>
    </Pressable>
  );
}

// Typing indicator replaces the generic spinner: three dots, staggered opacity loop.
function Typing({ reduced, color }) {
  const dots = useRef([0, 1, 2].map(() => new Animated.Value(0.3))).current;
  useEffect(() => {
    if (reduced) return;
    const loops = dots.map((d, i) =>
      Animated.loop(Animated.sequence([
        Animated.delay(i * 150),
        Animated.timing(d, { toValue: 1, duration: 400, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.timing(d, { toValue: 0.3, duration: 400, easing: Easing.inOut(Easing.ease), useNativeDriver: true }),
        Animated.delay(300 - i * 150),
      ])));
    loops.forEach((l) => l.start());
    return () => loops.forEach((l) => l.stop());
  }, [reduced]);
  return (
    <View style={{ flexDirection: "row", gap: 5, padding: 14 }} accessibilityLabel="Escribiendo">
      {dots.map((d, i) => <Animated.View key={i} style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: color, opacity: d }} />)}
    </View>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [image, setImage] = useState(null); // { uri, base64 }
  const [local, setLocal] = useState(false);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [speak, setSpeak] = useState(false);
  const [tab, setTab] = useState("deals"); // "deals" | "chat"
  const list = useRef(null);
  const reduced = useReducedMotion();
  const c = palette[useColorScheme() === "dark" ? "dark" : "light"];
  const s = useMemo(() => styles(c), [c]);

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
        <Text style={s.title}>DealFinder AI</Text>
        <View style={s.tabs}>
          {[["deals", "Ofertas"], ["chat", "Asistente"]].map(([k, label]) => (
            <Pressable key={k} onPress={() => setTab(k)} accessibilityRole="tab" accessibilityState={{ selected: tab === k }} style={[s.tab, tab === k && s.tabOn]}>
              <Text style={[s.tabText, tab === k && { color: "#fff" }]}>{label}</Text>
            </Pressable>
          ))}
        </View>
        {tab === "chat" && <View style={s.row}>
          <Text style={s.label}>Local</Text>
          <Switch value={local} onValueChange={toggleLocal} disabled={busy} trackColor={{ true: c.accent }} />
          <Text style={[s.label, { marginLeft: 16 }]}>Voz</Text>
          <Switch value={speak} onValueChange={setSpeak} trackColor={{ true: c.accent }} />
        </View>}
      </View>
      {tab === "deals" ? <Deals c={c} /> : <>
      {!!status && <Text style={s.status}>{status}</Text>}
      {messages.length === 0 && (
        <View style={s.empty} pointerEvents="none">
          <Text style={s.emptyTitle}>¿En qué le ayudo?</Text>
          <Text style={s.emptyBody}>Escriba un mensaje o adjunte una foto.</Text>
        </View>
      )}
      <FlatList
        ref={list}
        data={messages}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={{ padding: 16, flexGrow: 1 }}
        renderItem={({ item }) => (
          <Enter reduced={reduced} style={[s.bubble, item.role === "user" ? s.user : s.bot]}>
            {item.uri && <Image source={{ uri: item.uri }} style={s.img} />}
            <Text style={item.role === "user" ? s.userText : s.botText}>{item.content}</Text>
          </Enter>
        )}
        ListFooterComponent={busy && !status ? <View style={[s.bubble, s.bot, { padding: 0 }]}><Typing reduced={reduced} color={c.muted} /></View> : null}
      />
      {image && <Image source={{ uri: image.uri }} style={s.preview} />}
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <View style={s.inputRow}>
          <PressScale onPress={pickImage} disabled={local} reduced={reduced} label="Adjuntar foto" style={s.ghost}>
            <Text style={s.ghostText}>+</Text>
          </PressScale>
          <TextInput
            style={s.input}
            value={input}
            onChangeText={setInput}
            placeholder="Escriba un mensaje…"
            placeholderTextColor={c.muted}
            onSubmitEditing={send}
            multiline
          />
          <PressScale onPress={send} disabled={busy} reduced={reduced} label="Enviar" style={s.send}>
            <Text style={s.sendText}>↑</Text>
          </PressScale>
        </View>
      </KeyboardAvoidingView>
      </>}
    </SafeAreaView>
  );
}

const styles = (c) => StyleSheet.create({
  root: { flex: 1, backgroundColor: c.bg },
  bar: { paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: c.line },
  row: { flexDirection: "row", alignItems: "center", marginTop: 6 },
  tabs: { flexDirection: "row", gap: 8, marginTop: 8 },
  tab: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 16, backgroundColor: c.surface },
  tabOn: { backgroundColor: c.accent },
  tabText: { fontSize: 14, fontWeight: "600", color: c.text },
  title: { fontSize: 22, fontWeight: "700", letterSpacing: -0.4, color: c.text },
  label: { fontSize: 14, color: c.muted, marginRight: 6 },
  status: { paddingHorizontal: 16, paddingVertical: 8, color: c.muted },
  empty: { position: "absolute", top: "35%", left: 0, right: 0, alignItems: "center", paddingHorizontal: 32 },
  emptyTitle: { fontSize: 24, fontWeight: "700", letterSpacing: -0.5, color: c.text },
  emptyBody: { marginTop: 6, fontSize: 15, color: c.muted, textAlign: "center" },
  bubble: { maxWidth: "85%", paddingHorizontal: 14, paddingVertical: 10, borderRadius: 18, marginBottom: 8 },
  user: { alignSelf: "flex-end", backgroundColor: c.accent, borderBottomRightRadius: 6 },
  userText: { color: "#fff", fontSize: 16, lineHeight: 22 },
  bot: { alignSelf: "flex-start", backgroundColor: c.surface, borderBottomLeftRadius: 6 },
  botText: { color: c.text, fontSize: 16, lineHeight: 22 },
  img: { width: 160, height: 160, borderRadius: 12, marginBottom: 6 },
  preview: { width: 64, height: 64, marginHorizontal: 16, marginBottom: 8, borderRadius: 12 },
  inputRow: { flexDirection: "row", alignItems: "flex-end", paddingHorizontal: 12, paddingVertical: 8, borderTopWidth: StyleSheet.hairlineWidth, borderColor: c.line },
  input: { flex: 1, backgroundColor: c.surface, color: c.text, borderRadius: 20, paddingHorizontal: 14, paddingTop: 10, paddingBottom: 10, marginHorizontal: 8, maxHeight: 120, fontSize: 16 },
  ghost: { width: 40, height: 40, borderRadius: 20, backgroundColor: c.surface, alignItems: "center", justifyContent: "center" },
  ghostText: { fontSize: 24, color: c.text, marginTop: -2 },
  send: { width: 40, height: 40, borderRadius: 20, backgroundColor: c.accent, alignItems: "center", justifyContent: "center" },
  sendText: { fontSize: 20, fontWeight: "700", color: "#fff" },
});
