from .mycog import FrameCog


async def setup(bot):
    
    await bot.add_cog(FrameCog(bot))
