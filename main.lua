require "cairo" -- cairo graphic library
local cjson = require "cjson"


--  the funtion which will be called at the beginning of the run, used to setup a few global values
function conky_setup(  )

end


function trim1(s)
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end


function conky_main(  )

	-- if no conky window then exit
	if conky_window == nil then return end

	-- the number of update
	local updates = tonumber(conky_parse("${updates}"));
	-- if not third update exit
	if updates < 3 then return end

	-- prepare cairo drawing surface
	local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height);
	cr = cairo_create(cs);
	local cj = cjson.new();

	-- for position text
	local extents = cairo_text_extents_t:create();
	local text = "";


  -- lets add some control variables
  local total_width = 300;
  local height = 400;


  -- now the background
  cairo_set_source_rgba(cr, 1, 1, 1, 1);
  cairo_rectange







	-- destroying the cairo surface
	cairo_destroy(cr);
	cairo_surface_destroy(cs);
	cr=nil;
end