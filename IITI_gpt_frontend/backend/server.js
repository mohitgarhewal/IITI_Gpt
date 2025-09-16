const express = require("express")
const mongoose = require("mongoose")
const cors = require("cors")
const bcrypt = require("bcryptjs")
const jwt = require("jsonwebtoken")
require("dotenv").config()

const app = express()

// Middleware
app.use(cors())
app.use(express.json())

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || "mongodb://localhost:27017/iiti-gpt", {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})

// User Schema
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  name: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
})

// Chat Schema
const chatSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  title: { type: String, required: true },
  messages: [
    {
      role: { type: String, enum: ["user", "assistant"], required: true },
      content: { type: String, required: true },
      timestamp: { type: Date, default: Date.now },
    },
  ],
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
})

const User = mongoose.model("User", userSchema)
const Chat = mongoose.model("Chat", chatSchema)

// Auth Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers["authorization"]
  const token = authHeader && authHeader.split(" ")[1]

  if (!token) {
    return res.status(401).json({ error: "Access token required" })
  }

  jwt.verify(token, process.env.JWT_SECRET || "your-secret-key", (err, user) => {
    if (err) {
      return res.status(403).json({ error: "Invalid token" })
    }
    req.user = user
    next()
  })
}

// Auth Routes
app.post("/api/register", async (req, res) => {
  try {
    const { email, password, name } = req.body

    // Check if user exists
    const existingUser = await User.findOne({ email })
    if (existingUser) {
      return res.status(400).json({ error: "User already exists" })
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10)

    // Create user
    const user = new User({
      email,
      password: hashedPassword,
      name,
    })

    await user.save()

    // Generate token
    const token = jwt.sign({ userId: user._id, email: user.email }, process.env.JWT_SECRET || "your-secret-key", {
      expiresIn: "7d",
    })

    res.status(201).json({
      message: "User created successfully",
      token,
      user: { id: user._id, email: user.email, name: user.name },
    })
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

app.post("/api/login", async (req, res) => {
  try {
    const { email, password } = req.body

    // Find user
    const user = await User.findOne({ email })
    if (!user) {
      return res.status(400).json({ error: "Invalid credentials" })
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password)
    if (!isValidPassword) {
      return res.status(400).json({ error: "Invalid credentials" })
    }

    // Generate token
    const token = jwt.sign({ userId: user._id, email: user.email }, process.env.JWT_SECRET || "your-secret-key", {
      expiresIn: "7d",
    })

    res.json({
      message: "Login successful",
      token,
      user: { id: user._id, email: user.email, name: user.name },
    })
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

// Chat Routes
app.get("/api/chats", authenticateToken, async (req, res) => {
  try {
    const chats = await Chat.find({ userId: req.user.userId })
      .select("_id title createdAt updatedAt")
      .sort({ updatedAt: -1 })

    res.json(chats)
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

app.get("/api/chats/:chatId", authenticateToken, async (req, res) => {
  try {
    const chat = await Chat.findOne({
      _id: req.params.chatId,
      userId: req.user.userId,
    })

    if (!chat) {
      return res.status(404).json({ error: "Chat not found" })
    }

    res.json(chat)
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

app.post("/api/chats", authenticateToken, async (req, res) => {
  try {
    const { title, message } = req.body

    const chat = new Chat({
      userId: req.user.userId,
      title: title || "New Chat",
      messages: [
        {
          role: "user",
          content: message,
          timestamp: new Date(),
        },
      ],
    })

    await chat.save()
    res.status(201).json(chat)
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

app.post("/api/chats/:chatId/messages", authenticateToken, async (req, res) => {
  try {
    const { role, content } = req.body

    const chat = await Chat.findOne({
      _id: req.params.chatId,
      userId: req.user.userId,
    })

    if (!chat) {
      return res.status(404).json({ error: "Chat not found" })
    }

    chat.messages.push({
      role,
      content,
      timestamp: new Date(),
    })

    chat.updatedAt = new Date()
    await chat.save()

    res.json(chat)
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

app.delete("/api/chats/:chatId", authenticateToken, async (req, res) => {
  try {
    await Chat.findOneAndDelete({
      _id: req.params.chatId,
      userId: req.user.userId,
    })

    res.json({ message: "Chat deleted successfully" })
  } catch (error) {
    res.status(500).json({ error: "Server error" })
  }
})

const PORT = process.env.PORT || 5000
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
