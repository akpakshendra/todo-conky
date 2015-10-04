-- Author : Akshendra Pratap Singh
-- Date : 22 June @001
-- A todo desktop widget


require "cairo" -- cairo graphic library


-- thanks to dasblinkenlight (stackoverflow)
-- function explode slipts the string at spaces and put them into a table
-- @ s : string to explode
-- # words : a table of words
-- # count : the mumber of words
function explode(s)

  local words = {};
  local count = 0;

  -- split the string
  for value in string.gmatch(s,"[%w%p]+") do
    count = count + 1;
    words[count] = value;
  end

  return count, words;

end


-- this is the function used for printing single line of text
-- @ text : the text to print
-- @ x, y : the coordinated to print the text
-- @ size : the size of font to use
-- @ family : the font-family to use
-- @ text_ext, font_ext : the cairo text-extents and font_extents objects
-- @ options : the table of options specifying everything that need to layout the text this include
--      @ valign : the legal values are 0(for baseline which is the default), 1(for top) and 2(for center)
--      @ halign : the legal values are 0(for left which is the default), 1(for right) and 2(for center)
--      @ width : required in case of center and right halign
--      @ height : required in case of center and top valign
--      @ bold, italic : same as cairo_show_text
-- # final_x, final_y : the position where the text was printed
function lineText(text, x, y, size, family, text_ext, font_ext, options)

  -- if the options are not provided use the defalut
  if options == nil then
    options = {};
    options.valign = 0;
    options.halign = 0;
    options.bold = 0;
    options.italic = 0;
  end

  -- if bold in not given get default
  if options.bold == nil then
    options.bold = 0;
  end

  -- if italic is not passed use default
  if options.italic == nil then
    options.italic = 0;
  end

  -- if halign is not passed use default
  if options.halign == nil then
    options.halign = 0;
  end

  -- if halign is not passed use default
  if options.valign == nil then
    options.valign = 0;
  end

  -- set the font family and size of text
  cairo_set_font_size(cr, size);
  cairo_select_font_face(cr, family, options.bold, options.italic);

  -- get the extents of the text
  cairo_text_extents(cr, text, text_ext);
  cairo_font_extents(cr, font_ext);

  -- align the text horizontally
  local final_x = x;
  if options.halign == 0 then   -- for left align
    final_x = x;
  elseif options.halign == 1 then   -- for right align
    final_x = x + options.width - text_ext.width;
  elseif options.halign == 2 then   -- for center align
    final_x = x + options.width/2 - text_ext.width/2;
  end

  -- vertically align the text
  local final_y = y;
  if options.valign == 0 then   -- for baseline
    final_y = y;
  elseif options.valign == 1 then   -- for top
    final_y = y + font_ext.height;
  elseif options.valign == 2 then   -- for center
    final_y = y + options.height/2 + font_ext.height/2;
  end

  -- show the text finally
  cairo_move_to(cr, final_x, final_y - font_ext.descent);
  cairo_show_text(cr, text);

  -- return the final printing position
  return final_x + text_ext.width, final_y;

end


-- a function to print multiline text propery layout with word wrapping ofcourse
-- @ text : the text to print
-- @ x, y : the coordinated to print the text
-- @ width : the extent to which every line can be extended
-- @ size : the size of font to use
-- @ family : the font-family to use
-- @ text_ext, font_ext : the cairo text-extents and font_extents objects
-- @ options : the table of options specifying everything that need to layout the text this include
--      @ halign : the legal values are 0(for left which is the default), 1(for right) and 2(for center)
--      @ bold, italic : same as cairo_show_text
-- # final_x, y : the position where the text was printed
function multiText(text, x, y, width, height, size, family, text_ext, font_ext, options)

  -- first use explode to convert the text into array of words
  local count, words = explode(text);

  -- if the options are not provided use the defalut
  if options == nil then
    options = {};
    options.valign = 1;
    options.halign = 0;
    options.width = width;
    options.bold = 0;
    options.italic = 0;
  end

  -- if bold in not given get default
  if options.bold == nil then
    options.bold = 0;
  end

  -- if italic is not passed use default
  if options.italic == nil then
    options.italic = 0;
  end

  -- set up the options width anyways
  if options ~= nil then
    options.width = width;
  end


  -- set the font family and size of text
  cairo_set_font_size(cr, size);
  cairo_select_font_face(cr, family, options.bold, options.italic);

  -- now get the extents
  cairo_text_extents(cr, text, text_ext);
  cairo_font_extents(cr, font_ext);

  -- now find out the lines
  local no_of_lines = 1;
  local lines = {};
  lines[no_of_lines] = words[1];
  for i = 2, count do
    -- check if adding the next words will cross the width available
    cairo_text_extents(cr, lines[no_of_lines]..' '..words[i], text_ext);
    -- if not then add the word
    if text_ext.width <= width then
      lines[no_of_lines] =lines[no_of_lines]..' '..words[i];
    else
      no_of_lines = no_of_lines + 1;
      lines[no_of_lines] = words[i];
    end
  end

  local final_x;
  for i = 1, no_of_lines do
    final_x, y = lineText(lines[i], x, y , size, family, text_ext, font_ext, options);
  end

  return final_x, y, no_of_lines;

end


-- this function trims spaces from both side a string
-- @ s : the string to trim
-- # s : the trimed string
function trim1(s)
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end


-- a function to print the todo list, lets try writing that
function printTODO(settings, text_ext, font_ext)

  cairo_set_source_rgba(cr, 1, 1, 1, 1);

  -- variables for controling the ident
  local indent = 0;
  local x = settings.startx;
  local y = settings.starty;
  local line_points = {};
  local point_count = 0;
  local darts = {};
  local darts_count = 0;
  local nol;

  -- get an print the line according to markup
  local line = '';
  local i = 1;
  while i <= data_lines and y <= settings.starty + settings.height do
    -- print(i);
    line = data[i];

    -- if this was dateline
    if line == 'D' then
      indent = 0;
      i = i + 1;
      cairo_set_source_rgba(cr, 1, 1, 1, 1);
      x, y, _ = multiText(data[i], settings.startx + indent, y, settings.width, settings.height, 15, 'Poiret One', text_ext, font_ext);
      point_count = point_count + 1;
      line_points[point_count] = y;
      y = y + 5;
    end

    if line == 'T' then
      indent = 30;
      i = i + 1;
      cairo_set_source_rgba(cr, 1, 1, 1, 1);
      x, y, nol = multiText(data[i], settings.startx + indent, y, settings.width, settings.height, 12, 'Raleway', text_ext, font_ext);

      darts_count = darts_count + 1;
      darts[darts_count] = y - nol*font_ext.height + font_ext.height/2;

      if (data[i+1] == 'd') then
        y = y + 2;
      elseif (data[i+1] == 'T') then
        y = y + 5;
      else
        y = y + 10;
        point_count = point_count + 1;
        line_points[point_count] = y - 2;
      end
    end


    if line == 'd' then
      indent = 40;
      i = i + 1;
      cairo_set_source_rgba(cr, 0.7, 0.7, 0.7, 1);
      x, y = multiText(data[i], settings.startx + indent, y, settings.width, settings.height, 10, 'Archivo Narrow', text_ext, font_ext);
      if (data[i+1] == 'd') then
        y = y;
      elseif (data[i+1] == 'T') then
        y = y + 5;
      else
        y = y + 10;
        point_count = point_count + 1;
        line_points[point_count] = y - 2;
      end
    end

    i = i + 1;

  end

  cairo_set_source_rgba(cr, 0.7, 0.7, 0.7, 1);
  if point_count%2 ~= 0 then
    point_count = point_count + 1;
    line_points[point_count] = y;
  end

  -- print(point_count);
    -- print the vertical line
  local i = 1;
  while i <= point_count do
    cairo_move_to(cr, settings.startx + 15, line_points[i]);
    i = i + 1;
    cairo_line_to(cr, settings.startx + 15, line_points[i])
    i = i + 1;
    cairo_stroke(cr);
  end

  for i = 1, darts_count do
    cairo_arc(cr, settings.startx+15 , darts[i], 5, 0, 2*math.pi);
    cairo_fill(cr);
  end

end





--  the funtion which will be called at the beginning of the run, used to setup a few global values
function conky_setup(  )

  -- get the data from the data file
  data = {};
  data_lines = 0;
  for line in io.lines('data') do
    data_lines = data_lines + 1;
    data[data_lines] = line;
  end

end


-- the function that is called every time the script is run
function conky_main(  )

	-- if no conky window then exit
	if conky_window == nil then return end

	-- the number of update
	local updates = tonumber(conky_parse("${updates}"));
	-- if not third update exit
	if updates < 1 then return end

	-- prepare cairo drawing surface
	local cs = cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height);
	cr = cairo_create(cs);

	-- for position text
	local text_ext = cairo_text_extents_t:create();
  local font_ext = cairo_font_extents_t:create();
	local text = "";

  -- lets add some control variables
  local settings = {};
  settings.width = 250;
  settings.height = 500;
  settings.shadow = 5;
  settings.startx = 50;
  settings.starty = 330;

  -- call the function that prints the list
  cairo_set_source_rgba(cr, 1, 1, 1, 1);
  printTODO(settings, text_ext, font_ext);

	-- destroying the cairo surface
	cairo_destroy(cr);
	cairo_surface_destroy(cs);
	cr=nil;
end