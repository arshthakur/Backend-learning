
import connectDB from "./db/index.js";
import  dotenv  from "dotenv";


dotenv.config({
  path:'./env'
})

connectDB()
.then(()=>{
  app.listen(process.env.PORT||8000,()=>{
   console.log(`listen at port : ${process.env.Port}`)
  })
})
.catch((err)=>{
  console.log("MongoDB connection failed!!!",err);
})