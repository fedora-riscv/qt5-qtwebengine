#!/bin/bash
# Copyright 2017 Kevin Kofler <Kevin@tigcc.ticalc.org>
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

if [ -z "$2" ] ; then
  echo "usage: ./snapshot_qtwebengine.sh COMMIT VERSION"
  echo "e.g.: ./snapshot_qtwebengine.sh ee719ad313e564d4e6f06d74b313ae179169466f 5.6.3"
  exit 1
fi

COMMIT="$1"
VERSION="$2"

SRCDIRNAME="qtwebengine-git"
DIRNAME="qtwebengine-opensource-src-$VERSION"

echo "checking out git://code.qt.io/qt/qtwebengine.git"
rm -rf "$SRCDIRNAME" || exit $?
git clone --recurse-submodules git://code.qt.io/qt/qtwebengine.git \
    "$SRCDIRNAME" || exit $?

echo "exporting revision $COMMIT to $DIRNAME"
rm -rf "$DIRNAME" || exit $?
BASEDIR=`pwd`
cd "$SRCDIRNAME" || exit $?
git reset --hard "$COMMIT" || exit $?
git archive --format=tar --prefix="$DIRNAME/" "$COMMIT" | tar -x -C "$BASEDIR" \
  || exit $?
git submodule foreach --recursive \
    'git archive --format=tar --prefix="'"$DIRNAME"'/$path/" "$sha1" | tar -x -C "'"$BASEDIR"'"' \
  || exit $?
cd .. || exit $?
rm -rf "$SRCDIRNAME" || exit $?

echo "running syncqt.pl in $DIRNAME"
cd "$DIRNAME" || exit $?
syncqt.pl -version "$VERSION" sync.profile || exit $?
cd .. || exit $?

echo "creating $DIRNAME.tar.xz"
XZ_OPT="-9 -f" tar cJf "$DIRNAME.tar.xz" "$DIRNAME" || exit $?

echo "running ./clean_qtwebengine.sh $VERSION"
./clean_qtwebengine.sh "$VERSION" || exit $?

echo "renaming $DIRNAME.tar.xz to $DIRNAME-$COMMIT.tar.xz"
mv "$DIRNAME.tar.xz" "$DIRNAME-$COMMIT.tar.xz" || exit $?

echo "renaming $DIRNAME-clean.tar.xz to $DIRNAME-$COMMIT-clean.tar.xz"
mv "$DIRNAME-clean.tar.xz" "$DIRNAME-$COMMIT-clean.tar.xz" || exit $?

echo "done"
exit 0
