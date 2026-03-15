const jwt = require("jsonwebtoken")

const JWT_SECRET = process.env.JWT_SECRET || "visionestate-secret-key"

exports.protect = (req, res, next) => {
  const authHeader = req.headers.authorization || ""

  if (!authHeader.startsWith("Bearer ")) {
    res.status(401).json({ error: "Authorization token missing" })
    return
  }

  const token = authHeader.split(" ")[1]

  try {
    const decoded = jwt.verify(token, JWT_SECRET)
    req.user = decoded
    next()
  } catch (error) {
    res.status(401).json({ error: "Invalid or expired token" })
  }
}
