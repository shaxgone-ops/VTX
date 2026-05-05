import { useEffect, useMemo, useState } from "react"

type CardRow = {
  card_id: number
  code: string
  title: string
  rarity: string
  image_url: string
  stage: number
  max_stage: number
  current_profit: number
  next_profit: number
  next_cost: number
}

type CardsResponse = {
  cards: CardRow[]
  profit_per_hour: number
  balance: number
}

const apiBase = import.meta.env.VITE_API_BASE_URL || ""

function getTelegramId(): number {
  const fromQuery = new URLSearchParams(window.location.search).get("telegram_id")
  if (fromQuery && /^\d+$/.test(fromQuery)) {
    return Number(fromQuery)
  }
  return 0
}

async function loadCards(telegramId: number): Promise<CardsResponse> {
  const response = await fetch(`${apiBase}/api/cards/${telegramId}`)
  if (!response.ok) {
    throw new Error("Failed to load cards")
  }
  return response.json()
}

async function upgradeCard(telegramId: number, cardId: number): Promise<void> {
  const response = await fetch(`${apiBase}/api/cards/upgrade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ telegram_id: telegramId, card_id: cardId })
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Upgrade failed" }))
    throw new Error(payload.detail || "Upgrade failed")
  }
}

function rarityClass(rarity: string): string {
  if (rarity === "legendary") return "border-amber-400"
  if (rarity === "epic") return "border-fuchsia-400"
  if (rarity === "rare") return "border-cyan-300"
  return "border-slate-300"
}

function CardsMarket() {
  const telegramId = useMemo(() => getTelegramId(), [])
  const [data, setData] = useState<CardsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [busyCardId, setBusyCardId] = useState<number | null>(null)
  const [error, setError] = useState("")

  const refresh = async () => {
    if (!telegramId || !apiBase) {
      setError("Missing telegram_id or VITE_API_BASE_URL")
      setLoading(false)
      return
    }
    setLoading(true)
    try {
      const payload = await loadCards(telegramId)
      setData(payload)
      setError("")
    } catch (err) {
      const message = err instanceof Error ? err.message : "Load failed"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void refresh()
  }, [])

  const onUpgrade = async (cardId: number) => {
    setBusyCardId(cardId)
    try {
      await upgradeCard(telegramId, cardId)
      await refresh()
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upgrade failed"
      setError(message)
    } finally {
      setBusyCardId(null)
    }
  }

  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-16 sm:px-8 lg:px-12">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <h2 className="font-rubik text-3xl font-bold uppercase tracking-tight">Cards Market</h2>
        <div className="flex flex-wrap gap-3 text-sm sm:text-base">
          <span className="rounded-md bg-slate-800 px-4 py-2">Balance: {data ? data.balance.toFixed(2) : "0.00"}</span>
          <span className="rounded-md bg-slate-800 px-4 py-2">Profit/H: {data ? data.profit_per_hour.toFixed(2) : "0.00"}</span>
        </div>
      </div>

      {loading && <div className="rounded-lg bg-slate-900 p-6">Loading cards...</div>}
      {error && <div className="mb-5 rounded-lg bg-red-900/40 p-4 text-red-200">{error}</div>}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {(data?.cards || []).map((card) => (
          <article
            key={card.card_id}
            className={`overflow-hidden rounded-xl border bg-slate-900 shadow-xl ${rarityClass(card.rarity)}`}
          >
            <img src={card.image_url} alt={card.title} className="h-48 w-full object-cover" />
            <div className="space-y-3 p-4">
              <div className="flex items-start justify-between">
                <h3 className="font-rubik text-lg font-bold uppercase">{card.title}</h3>
                <span className="rounded bg-slate-800 px-2 py-1 text-xs uppercase">{card.rarity}</span>
              </div>
              <div className="text-sm text-slate-200">Stage: {card.stage}/{card.max_stage}</div>
              <div className="text-sm text-slate-200">Current PPH: {card.current_profit.toFixed(2)}</div>
              <div className="text-sm text-slate-200">Next PPH: {card.next_profit.toFixed(2)}</div>
              <div className="text-sm text-slate-200">Upgrade Cost: {card.next_cost.toFixed(2)}</div>
              <button
                type="button"
                disabled={busyCardId === card.card_id || card.stage >= card.max_stage}
                onClick={() => onUpgrade(card.card_id)}
                className="w-full rounded-md bg-white px-4 py-3 font-rubik text-sm font-bold uppercase text-[#161a20] transition hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {card.stage >= card.max_stage ? "Max Stage" : busyCardId === card.card_id ? "Processing" : "Upgrade"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

export default CardsMarket
