import mongoose, {model, schema} from "mongoose";
import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";

const userSchema = new mongoose.Schema({
  userName:{
   type:String,
   required:true,
   unique:true,
   lowercase:true,
   index:true,
   trim:true
  },
  email:{
   type:String,
   required:true,
   unique:true,
   lowercase:true,
   trim:true
  },
  fullName:{
   type:String,
   trim:true,
   required:true,
   index:true
  },
  avatar:{
    type:String,     // cloudinary Url
    required:true,
  },
  coverImage:{
    type:String,            // cloudinary url
    required:true,
  },
  watchHistory:[{
    type:mongoose.Schema.Types.ObjectId,
    ref:"watchHistory"
  }],
  password:{
    type:String,
    required:[true, "password is required"]
  },
  refreshToken:{
    type:String
  }
},{TimeStamps:true})

userSchema.pre("save", async function(next){
  if(!this.isModified("password")) return next();

  this.password = bcrypt.hash(this.password,10)
  next()
})

userSchema.methods.isPasswordCorrect = async function(password){
     return await bcrypt.compare(password, this.password)
}
userSchema.methods.generateAccessTokens = function(){
      jwt.sign(
        {
          _id: this._id,
          userName: this.userName,
          email:this.email,
          fullName: this.fullName
        },
        process.env.ACCESS_TOKEN_SECRET,{
          expiresIn: process.env.ACCESS_TOKEN_EXPIRY
        }
      )
}
userSchema.methods.generateRefreshTokens = function(){
  jwt.sign(
    {
      _id: this._id,
    },
    process.env.REFRESH_TOKEN_SECRET,{
      expiresIn: process.env.REFRESH_TOKEN_EXPIRY
    }
  )
}

export const User = mongoose.model("user", userSchema)
