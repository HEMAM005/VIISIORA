const bcrypt = require("bcrypt")
const jwt = require("jsonwebtoken")

const User = require("../models/User")

const JWT_SECRET = process.env.JWT_SECRET || "visionestate-secret-key"
const EMAIL_PATTERN = /@/
const PASSWORD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$/

const signToken = (user) =>
  jwt.sign(
    {
      id: user._id.toString(),
      email: user.email,
      name: user.name
    },
    JWT_SECRET,
    { expiresIn: "7d" }
  )

exports.register = async (req, res) => {
  try {
    const name = (req.body.name || "").trim().toUpperCase()
    const email = (req.body.email || "").trim().toLowerCase()
    const password = req.body.password || ""

    if (!name) {
      res.status(400).json({ error: "Name is required" })
      return
    }

    if (!EMAIL_PATTERN.test(email)) {
      res.status(400).json({ error: "Email must contain @" })
      return
    }

    if (!PASSWORD_PATTERN.test(password)) {
      res.status(400).json({
        error:
          "Password must be at least 8 characters and include uppercase, lowercase, number, and special character"
      })
      return
    }

    const existingUser = await User.findOne({ email })

    if (existingUser) {
      res.status(409).json({ error: "User already exists with this email" })
      return
    }

    const hashedPassword = await bcrypt.hash(password, 10)

    const user = await User.create({
      name,
      email,
      password: hashedPassword
    })

    const token = signToken(user)

    res.status(201).json({
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email
      }
    })
  } catch (error) {
    console.error(error)
    res.status(500).json({ error: "Registration failed" })
  }
}

exports.login = async (req, res) => {
  try {
    const email = (req.body.email || "").trim().toLowerCase()
    const password = req.body.password || ""

    const user = await User.findOne({ email })

    if (!user) {
      res.status(401).json({ error: "Invalid email or password" })
      return
    }

    const passwordMatches = await bcrypt.compare(password, user.password)

    if (!passwordMatches) {
      res.status(401).json({ error: "Invalid email or password" })
      return
    }

    const token = signToken(user)

    res.json({
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email
      }
    })
  } catch (error) {
    console.error(error)
    res.status(500).json({ error: "Login failed" })
  }
}

exports.getCurrentUser = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select("-password")

    if (!user) {
      res.status(404).json({ error: "User not found" })
      return
    }

    res.json(user)
  } catch (error) {
    console.error(error)
    res.status(500).json({ error: "Failed to fetch user" })
  }
}
