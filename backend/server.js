const express = require("express")
const cors = require("cors")
const path = require("path")

const connectDB = require("./config/db")

const authRoutes = require("./routes/authRoutes")
const imageRoutes = require("./routes/imageRoutes")

const app = express()
const uploadsDirectory = path.join(__dirname, "uploads")

connectDB()

app.use(cors())
app.use(express.json())

app.use("/api/auth", authRoutes)
app.use("/api/images", imageRoutes)
app.use("/uploads", express.static(uploadsDirectory))

const PORT = process.env.PORT || 5000

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
