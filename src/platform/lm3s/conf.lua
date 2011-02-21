-- Configuration file for the LM3S microcontroller

specific_files = "startup_gcc.c platform.c uart.c sysctl.c gpio.c ssi.c timer.c pwm.c ethernet.c systick.c flash.c interrupt.c cpu.c adc.c can.c platform_int.c"

local board = comp.board:upper()
if board == 'EK-LM3S1968' or board == 'EK-LM3S6965' or board == 'EK-LM3S8962' then
  specific_files = specific_files .. " rit128x96x4.c disp.c"
  addm 'ENABLE_DISP' 
end

-- The default for the Eagle 100 board is to start the image at 0x2000,
-- so that the built in Ethernet boot loader can be used to upload it
if board == 'EAGLE-100' then
  addlf '-Wl,-Ttext,0x2000'
end

local ldscript = board == 'EK-LM3S9B92' and "lm3s-9b92.ld" or "lm3s.ld"

-- Prepend with path
specific_files = utils.prepend_path( specific_files, sf( "src/platform/%s", platform) )
specific_files = specific_files .. " src/platform/cortex_utils.s src/platform/arm_cortex_interrupts.c"
ldscript = sf( "src/platform/%s/%s", platform, ldscript )

addm{ "FOR" .. comp.cpu:upper(), 'gcc', 'CORTEX_M3' }

-- Standard GCC flags
addcf{ '-ffunction-sections', '-fdata-sections', '-fno-strict-aliasing', '-Wall' }
addlf{ '-nostartfiles', '-nostdlib', '-T', ldscript, '-Wl,--gc-sections', '-Wl,--allow-multiple-definition' }
addaf{ '-x', 'assembler-with-cpp', '-Wall' }
addlib{ 'c','gcc','m' }

local target_flags =  {'-mcpu=cortex-m3','-mthumb' }

-- Configure general flags for target
addcf{ target_flags, '-mlittle-endian' }
addlf{ target_flags, '-Wl,-e,ResetISR', '-Wl,-static' }
addaf( target_flags )

-- Toolset data
tools.lm3s = {}

-- Programming function
tools.lm3s.progfunc = function( target, deps )
  local outname = deps[ 1 ]:target_name()
  os.execute( sf( "%s %s", toolset.size, outname ) )
  print "Generating binary image..."
  os.execute( sf( "%s -O binary %s %s.bin", toolset.bin, outname, output ) )
  return 0
end

-- Array of file names that will be checked against the 'prog' target; their absence will force a rebuild
tools.lm3s.prog_flist = { output .. ".bin" }

-- We use 'gcc' as the assembler
toolset.asm = toolset.compile

