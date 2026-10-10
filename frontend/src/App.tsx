
import { useEffect, useRef, useState, type FormEvent } from "react"
import { TaskPanel, type Task } from "./TaskPanel"
import "./App.css"

type ChatMessage = {
  from: "user" | "agent"
  text: string
}

type AgentEvent =
  | { type: "tool_call"; name: string; arguments: Record<string, unknown> }
  | { type: "tool_result"; name: string; result: string }
  | { type: "text"; text: string }
  | { type: "error"; text: string }
  | { type: "done" }




export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [tasks, setTasks] = useState<Task[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)


  async function loadTasks() {
    const response = await fetch("/tasks")
    setTasks(await response.json())
  }

  useEffect(() => {
    loadTasks()
  }, [])


  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])                                   

  function addMessage(from: ChatMessage["from"], text: string) {
    setMessages((prev) => [...prev, { from, text }])
  }

  function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()                      
    if (!input.trim()) return                   

    setMessages((prev) => [...prev, { from: "user", text: input }])
    setInput("") // clear the text box
    askAgent(input)
  }

  function handleEvent(event: AgentEvent) {
    if (event.type === "tool_call") addMessage("agent", `🔧 Calling ${event.name}...`)
    else if (event.type === "tool_result") addMessage("agent", `✅ ${event.name} finished`)
    else if (event.type === "text" || event.type === "error") addMessage("agent", event.text)
    else if (event.type === "done") {
      setLoading(false)
      loadTasks() 
    }
  }

  async function askAgent(text: string) {
    setLoading(true)
    try {
      const response = await fetch("/agent/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      })
      if (!response.ok) throw new Error(`Server error ${response.status}`)

      const reader = response.body!.pipeThrough(new TextDecoderStream()).getReader()
      let buffer = ""

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buffer += value
        const parts = buffer.split("\n\n")
        buffer = parts.pop() ?? ""
        for (const part of parts) {
          if (part.startsWith("data: ")) {
            handleEvent(JSON.parse(part.slice("data: ".length)))
          }
        }
      }
    } catch {
      addMessage("agent", "Sorry, I encountered an error while processing your request.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="layout">
      <main className="chat">
      <h1>PM Agent</h1>

      <ul className="messages">
        {messages.map((message, i) => (
          <li key={i} className={message.from}>
            {message.text}
          </li>
        ))}
      </ul>
      <div ref={bottomRef} />


      <form onSubmit={send}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask your project manager..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
      </main>

      <TaskPanel tasks={tasks} />
    </div>
  )
}
