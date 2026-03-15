const express = require("express")
const router = express.Router()

const fs = require("fs")
const multer = require("multer")
const path = require("path")

const {
  analyzeImages,
  getCategoryImages
} = require("../controllers/imageController")
const { protect } = require("../middleware/authMiddleware")

const uploadsDirectory = path.join(__dirname, "..", "uploads")
fs.mkdirSync(uploadsDirectory, { recursive: true })

const storage = multer.diskStorage({

  destination: uploadsDirectory,

  filename: (req, file, cb) => {
    cb(null, Date.now() + "-" + file.originalname)
  }

})

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype && file.mimetype.startsWith("image/")) {
      cb(null, true)
      return
    }

    cb(new Error("Only image uploads are supported"))
  }
})

// Upload multiple images
router.post("/analyze-batch", protect, upload.array("images"), analyzeImages)

// Get images by room category
router.get("/category/:room", protect, getCategoryImages)

module.exports = router
