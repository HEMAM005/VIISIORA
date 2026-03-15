const mongoose = require("mongoose")

const ImageResultSchema = new mongoose.Schema({

  imageName: String,

  roomType: String,

  roomConfidence: Number,

  furniture: String,

  furnitureConfidence: Number,

  tags: [String],

  createdAt: {
    type: Date,
    default: Date.now
  }

})

module.exports = mongoose.model("ImageResult", ImageResultSchema)