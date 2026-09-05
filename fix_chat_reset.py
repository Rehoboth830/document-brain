with open("frontend-react/components/chat/ChatInterface.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Find the scroll useEffect and add the reset useEffect after it
old = """  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])"""

new = """  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  // Clear chat when a new document is loaded
  useEffect(() => {
    setMessages([])
  }, [session.name])"""

if old in content:
    content = content.replace(old, new)
    with open("frontend-react/components/chat/ChatInterface.tsx", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Fix applied: chat resets when new document loads")
else:
    # Show what we have around useEffect
    idx = content.find("useEffect")
    print("Pattern not found. Current useEffect area:")
    print(content[idx:idx+400])
