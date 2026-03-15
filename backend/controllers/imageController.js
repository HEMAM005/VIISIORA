const axios = require("axios")

const ImageResult = require("../models/ImageResult")
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://localhost:8000/analyze"

exports.analyzeImages = async (req, res) => {

  try {
    if (!req.files || req.files.length === 0) {
      res.status(400).json({ error: "Please upload at least one image" })
      return
    }

    const categorizedResults = {}

    for (const file of req.files) {

      const aiResponse = await axios.post(
        AI_SERVICE_URL,
        { image_path: file.path },
        { timeout: 60000 }
      )

      const result = aiResponse.data
      if (!result || result.error) {
        throw new Error(result?.error || `AI analysis failed for ${file.filename}`)
      }

      const saved = await ImageResult.create({

        imageName: file.filename,

        roomType: result.room_type,

        roomConfidence: result.room_confidence,

        furniture: result.furniture_detected,

        furnitureConfidence: result.furniture_confidence,

        tags: result.tags

      })

      const room = result.room_type

      if (!categorizedResults[room]) {
        categorizedResults[room] = []
      }

      categorizedResults[room].push(saved)

    }

    res.json(categorizedResults)

  } catch (error) {

    console.error(error)

    res.status(500).json({ error: "Batch analysis failed" })

  }

}


// Get images by room category
exports.getCategoryImages = async (req, res) => {

  try {

    const room = req.params.room

    const images = await ImageResult.find({ roomType: room }).sort({ createdAt: -1 })

    res.json(images)

  } catch (error) {

    res.status(500).json({ error: "Failed to fetch category images" })

  }

}
