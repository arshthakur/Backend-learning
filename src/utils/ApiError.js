class ApiError extends Error{
   constructor(
    statuscode,
    message = "something went wrong",
    errors=[],
    statck = ""
   ){
    super(message)
    this.statuscode = statuscode
    this.errors = errors
    this.data = null
    this.message = message
    this.success = false

    if(statck){
      this.stack = statck
    }
    else{
      Error.captureStackTrace(this, this.constructor)
    }

   }

}

export {ApiError}