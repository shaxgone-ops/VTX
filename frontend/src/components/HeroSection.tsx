const bgVideoUrl =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260206_044704_dd33cb15-c23f-4cfc-aa09-a0465d4dcb54.mp4"

function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-[#21346e]">
      <video
        className="absolute inset-0 h-full w-full object-cover"
        autoPlay
        loop
        muted
        playsInline
      >
        <source src={bgVideoUrl} type="video/mp4" />
      </video>

      <div className="relative z-10 min-h-screen w-full">
        <div className="container mx-auto px-5 sm:px-8 lg:px-12">
          <div className="pt-32 md:pt-40 lg:pt-48">
            <h1
              className="
                font-rubik
                text-6xl
                font-extrabold
                uppercase
                leading-[0.98]
                tracking-[-2px]
                text-white
                sm:text-7xl
                md:text-8xl
                lg:text-[100px]
                lg:tracking-[-4px]
              "
            >
              <span className="block">NEW ERA</span>
              <span className="block">OF DESIGN</span>
              <span className="block">STARTS NOW</span>
            </h1>

            <div className="mt-10">
              <button
                type="button"
                className="
                  relative
                  h-[65px]
                  w-[184px]
                  transform
                  transition
                  duration-200
                  hover:scale-105
                  active:scale-95
                "
              >
                <svg
                  className="absolute inset-0 h-full w-full"
                  viewBox="0 0 184 65"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden="true"
                >
                  <path
                    d="M14 0H170L184 14V51L170 65H14L0 51V14L14 0Z"
                    fill="white"
                  />
                </svg>
                <span
                  className="
                    relative
                    z-10
                    flex
                    h-full
                    w-full
                    items-center
                    justify-center
                    font-rubik
                    text-[20px]
                    font-bold
                    uppercase
                    tracking-[-0.8px]
                    text-[#161a20]
                  "
                >
                  GET STARTED
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default HeroSection
