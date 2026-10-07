import React, { useState, useMemo, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { View, Text, TextInput, Pressable, FlatList, Linking, ActivityIndicator, StyleSheet } from "react-native";
import { findDeals } from "./cloud";

const SUGGESTIONS = ["iPhone 15", "audífonos Sony WH-1000XM5", "laptop gamer", "freidora de aire"];

const COUNTRIES = ["", "México", "España", "Chile", "Argentina", "Colombia", "EE.UU."];
const FAV_KEY = "dealfinder:favs";

const money = (n, cur) => (n == null ? "—" : `${cur || "$"} ${n.toLocaleString("es")}`);

function scoreColor(score, c) {
  return score >= 75 ? c.good : score >= 50 ? c.warn : c.muted;
}

function DealCard({ d, c, s, fav, onFav }) {
  return (
    <Pressable
      onPress={() => Linking.openURL(d.url)}
      accessibilityRole="link"
      accessibilityLabel={`${d.title} en ${d.store}`}
      style={({ pressed }) => [s.card, pressed && { transform: [{ scale: 0.98 }] }]}
    >
      <View style={s.cardTop}>
        <Text style={s.store}>{d.store}</Text>
        <View style={{ flexDirection: "row", gap: 12 }}>
          <Text style={[s.score, { color: scoreColor(d.score, c) }]}>{d.score}/100</Text>
          <Pressable onPress={onFav} hitSlop={10} accessibilityRole="button" accessibilityLabel={fav ? "Quitar de favoritos" : "Guardar en favoritos"}>
            <Text style={{ fontSize: 18, color: fav ? c.accent : c.muted }}>{fav ? "★" : "☆"}</Text>
          </Pressable>
        </View>
      </View>
      <Text style={s.cardTitle} numberOfLines={2}>{d.title}</Text>
      <View style={s.priceRow}>
        <Text style={s.price}>{money(d.price, d.currency)}</Text>
        {d.originalPrice != null && <Text style={s.old}>{money(d.originalPrice, d.currency)}</Text>}
        {d.discountPct != null && d.discountPct > 0 && <Text style={s.badge}>-{d.discountPct}%</Text>}
      </View>
      {!!d.verdict && <Text style={s.verdict}>{d.verdict}</Text>}
    </Pressable>
  );
}

export default function Deals({ c }) {
  const s = useMemo(() => styles(c), [c]);
  const [query, setQuery] = useState("");
  const [deals, setDeals] = useState(null); // null = aún no se buscó
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [country, setCountry] = useState("");
  const [favs, setFavs] = useState([]);
  const [showFavs, setShowFavs] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(FAV_KEY).then((v) => v && setFavs(JSON.parse(v))).catch(() => {});
  }, []);

  const toggleFav = (d) => {
    const next = favs.some((f) => f.url === d.url) ? favs.filter((f) => f.url !== d.url) : [d, ...favs];
    setFavs(next);
    AsyncStorage.setItem(FAV_KEY, JSON.stringify(next)).catch(() => {});
  };

  const search = async (q = query) => {
    const text = q.trim();
    if (!text || busy) return;
    setQuery(text);
    setBusy(true);
    setError("");
    try {
      setDeals(await findDeals(text, country));
    } catch (e) {
      setDeals(null);
      setError("No se pudo buscar: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={s.root}>
      <View style={s.searchRow}>
        <TextInput
          style={s.input}
          value={query}
          onChangeText={setQuery}
          placeholder="¿Qué quiere comprar?"
          placeholderTextColor={c.muted}
          returnKeyType="search"
          onSubmitEditing={() => search()}
        />
        <Pressable onPress={() => search()} disabled={busy} accessibilityRole="button" accessibilityLabel="Buscar ofertas" style={[s.go, busy && { opacity: 0.4 }]}>
          <Text style={s.goText}>Buscar</Text>
        </Pressable>
      </View>

      <View style={s.chips2}>
        {COUNTRIES.map((x) => (
          <Pressable key={x} onPress={() => setCountry(x)} style={[s.chip, country === x && s.chipOn]} accessibilityRole="button" accessibilityState={{ selected: country === x }}>
            <Text style={[s.chipText, country === x && { color: "#fff" }]}>{x || "Todos"}</Text>
          </Pressable>
        ))}
        <Pressable onPress={() => setShowFavs(!showFavs)} style={[s.chip, showFavs && s.chipOn]} accessibilityRole="button">
          <Text style={[s.chipText, showFavs && { color: "#fff" }]}>★ Favoritos ({favs.length})</Text>
        </Pressable>
      </View>

      {showFavs ? (
        <FlatList
          data={favs}
          keyExtractor={(d) => d.url}
          contentContainerStyle={{ padding: 16 }}
          renderItem={({ item }) => <DealCard d={item} c={c} s={s} fav onFav={() => toggleFav(item)} />}
          ListEmptyComponent={<Text style={[s.hint, { textAlign: "center", marginTop: 40 }]}>Aún no guardó ofertas.</Text>}
        />
      ) : <>
      {busy && (
        <View style={s.center}>
          <ActivityIndicator color={c.accent} />
          <Text style={s.hint}>Comparando tiendas…</Text>
        </View>
      )}
      {!!error && <Text style={s.error}>{error}</Text>}

      {!busy && deals === null && !error && (
        <View style={s.center}>
          <Text style={s.emptyTitle}>Encuentre el mejor precio</Text>
          <Text style={s.hint}>La IA compara tiendas y descarta falsos descuentos.</Text>
          <View style={s.chips}>
            {SUGGESTIONS.map((x) => (
              <Pressable key={x} onPress={() => search(x)} style={s.chip} accessibilityRole="button">
                <Text style={s.chipText}>{x}</Text>
              </Pressable>
            ))}
          </View>
        </View>
      )}

      {!busy && deals && (
        <FlatList
          data={deals}
          keyExtractor={(d) => d.url}
          contentContainerStyle={{ padding: 16 }}
          renderItem={({ item }) => <DealCard d={item} c={c} s={s} fav={favs.some((f) => f.url === item.url)} onFav={() => toggleFav(item)} />}
          ListEmptyComponent={<Text style={[s.hint, { textAlign: "center", marginTop: 40 }]}>No encontré ofertas fiables para esa búsqueda.</Text>}
        />
      )}
      </>}
    </View>
  );
}

const styles = (c) => StyleSheet.create({
  root: { flex: 1 },
  searchRow: { flexDirection: "row", padding: 12, gap: 8 },
  input: { flex: 1, backgroundColor: c.surface, color: c.text, borderRadius: 20, paddingHorizontal: 14, paddingVertical: 10, fontSize: 16 },
  go: { backgroundColor: c.accent, borderRadius: 20, paddingHorizontal: 16, justifyContent: "center" },
  goText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  center: { alignItems: "center", paddingTop: 48, paddingHorizontal: 32, gap: 8 },
  emptyTitle: { fontSize: 22, fontWeight: "700", letterSpacing: -0.4, color: c.text },
  hint: { fontSize: 15, color: c.muted, textAlign: "center" },
  error: { color: c.bad, padding: 16, textAlign: "center" },
  chips: { flexDirection: "row", flexWrap: "wrap", gap: 8, justifyContent: "center", marginTop: 16 },
  chips2: { flexDirection: "row", flexWrap: "wrap", gap: 6, paddingHorizontal: 12 },
  chipOn: { backgroundColor: c.accent },
  chip: { backgroundColor: c.surface, borderRadius: 16, paddingHorizontal: 12, paddingVertical: 8 },
  chipText: { color: c.text, fontSize: 14 },
  card: { backgroundColor: c.surface, borderRadius: 16, padding: 14, marginBottom: 10 },
  cardTop: { flexDirection: "row", justifyContent: "space-between" },
  store: { color: c.muted, fontSize: 13 },
  score: { fontSize: 13, fontWeight: "700" },
  cardTitle: { color: c.text, fontSize: 16, fontWeight: "600", marginTop: 4 },
  priceRow: { flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 8 },
  price: { color: c.text, fontSize: 22, fontWeight: "700", letterSpacing: -0.4 },
  old: { color: c.muted, fontSize: 14, textDecorationLine: "line-through" },
  badge: { color: c.good, fontWeight: "700", fontSize: 14 },
  verdict: { color: c.muted, fontSize: 14, lineHeight: 20, marginTop: 8 },
});
