with open("components/ui/Sidebar.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Replace Github import and usage
content = content.replace(
    'import { Github, Cpu, Database, Zap } from "lucide-react"',
    'import { Code2, Cpu, Database, Zap } from "lucide-react"'
)
content = content.replace("<Github size={12} />", "<Code2 size={12} />")

with open("components/ui/Sidebar.tsx", "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

# Verify
if "Github" in content:
    print("WARNING: Github still present in file")
else:
    print("Fixed: Github replaced with Code2 successfully")

# Show the import line
for i, line in enumerate(content.split("\n")[:6], 1):
    print(str(i) + ": " + line)
