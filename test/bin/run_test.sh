#!/bin/bash

echo
TESTROOT=$1
TESTBED=$2
TESTGROUP=$3
TESTNAME=$4
OPTIONS=$5
echo Start test $TESTNAME

# create testbed
echo Create testbed...
mkdir "$TESTBED/$TESTNAME"
cp bin/* "$TESTROOT/$TESTGROUP/$TESTNAME/data"/* "$TESTBED/$TESTNAME"

if [ -e "$TESTROOT/$TESTGROUP/options.txt" ]
then
    GROUP_OPTIONS=$(<"$TESTROOT/$TESTGROUP/options.txt")
fi

if [ -e "$TESTROOT/$TESTGROUP/$TESTNAME/data/options.txt" ]
then
    TEST_OPTIONS=$(<"$TESTROOT/$TESTGROUP/$TESTNAME/data/options.txt")
fi

# execute program
NUM_FAIL=0

if [ -e "$TESTROOT/$TESTGROUP/$TESTNAME/ref/list.txt" ]
then
    echo List program with options $GROUP_OPTIONS $TEST_OPTIONS
    cd "$TESTBED/$TESTNAME"
    python3 mpk.py --list <stdin.txt >list.txt $GROUP_OPTIONS $TEST_OPTIONS
    cd ../..

    echo Compare list...
    diff "$TESTROOT/$TESTGROUP/$TESTNAME/ref/list.txt" "$TESTBED/$TESTNAME/list.txt"
    ((ECODE=$?))

    if [ $ECODE -ne 0 ]
    then
	((NUM_FAIL+=1))
	cp "$TESTBED/$TESTNAME/list.txt" "$TESTROOT/$TESTGROUP/$TESTNAME/ref/list.txt"
    fi
fi

if [ -e "$TESTROOT/$TESTGROUP/$TESTNAME/ref/schedule.txt" ]
then
    echo Schedule program with options $GROUP_OPTIONS $TEST_OPTIONS
    cd "$TESTBED/$TESTNAME"
    python3 mpk.py --schedule <stdin.txt >schedule.txt $GROUP_OPTIONS $TEST_OPTIONS
    cd ../..

    echo Compare schedule...
    diff "$TESTROOT/$TESTGROUP/$TESTNAME/ref/schedule.txt" "$TESTBED/$TESTNAME/schedule.txt"
    ((ECODE=$?))

    if [ $ECODE -ne 0 ]
    then
	((NUM_FAIL+=1))
	cp "$TESTBED/$TESTNAME/schedule.txt" "$TESTROOT/$TESTGROUP/$TESTNAME/ref/schedule.txt"
    fi
fi


echo End test $TESTNAME
exit $NUM_FAIL
