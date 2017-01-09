
python setup.py build -c mingw32 --force
cp ./build/lib.win32-2.7/pypop.pyd ../pypop_dist -force

cp ../poppler-0.50/bin/freetype6.dll       ../pypop_dist -force
cp ../poppler-0.50/bin/jpeg62.dll          ../pypop_dist -force
cp ../poppler-0.50/bin/libcairo-2.dll      ../pypop_dist -force
cp ../poppler-0.50/bin/libexpat-1.dll      ../pypop_dist -force
cp ../poppler-0.50/bin/libfontconfig-1.dll ../pypop_dist -force
cp ../poppler-0.50/bin/libgcc_s_dw2-1.dll  ../pypop_dist -force
cp ../poppler-0.50/bin/libpixman-1-0.dll   ../pypop_dist -force
cp ../poppler-0.50/bin/libpng16-16.dll     ../pypop_dist -force
cp ../poppler-0.50/bin/libpoppler-cpp.dll  ../pypop_dist -force
cp ../poppler-0.50/bin/libpoppler.dll      ../pypop_dist -force
cp ../poppler-0.50/bin/libstdc++-6.dll     ../pypop_dist -force
cp ../poppler-0.50/bin/libtiff3.dll        ../pypop_dist -force
cp ../poppler-0.50/bin/zlib1.dll           ../pypop_dist -force

cp libiconv-2.dll ../pypop_dist -force

