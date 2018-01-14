//bouncer -- random on the first one, replace with 1/(5*log(thing)) probability

/**********************************************************/
/********************** metadata **************************/
/**********************************************************/

field_list hash_list {
    hh_meta.mKeyCarried;
}

field_list_calculation stage2_hash {
    input {
        hash_list;
    }
    algorithm : my_hash_2;
    output_width : 5;
}

header_type tracking_metadata_t {
    fields {
        bit<32> mKeyInTable;
        bit<32> mCountInTable;
        bit<5> mIndex;
        bit<1> mValid;
        bit<32> mKeyCarried;
        bit<32> mCountCarried;
        bit<32> mDiff;
        bit<7> mRand;
        bit<7> mLog;
    }
}

metadata tracking_metadata_t hh_meta;

/***************************************************************/
/********************** table stage 1 **************************/
/***************************************************************/

register flow_tracker_stage1 {
    width: 32;
    static: track_stage1;
    instance_count: 32;
}

register packet_counter_stage1 {
    width: 32;
    static: track_stage1;
    instance_count: 32;
}

register valid_bit_stage1 {
    width: 1;
    static: track_stage1;
    instance_count: 32;
}

// <=1: 66
// 2: 42
// 3: 33
// 4: 29
// 5-6: 25
// 7-10: 21
// 11-14: 18
// 15-20: 16
// 21-50: 13
// 51-100: 11
// 101-200: 9
// 201-700: 7
// 701 - 5000: 6
// 5000 - 100000: 5
// 100001 and greater = 4

action do_stage1(){
    // first table stage
    hh_meta.mKeyCarried = ipv4.srcAddr;
    hh_meta.mCountCarried = 0;

    // generate random value
    modify_field_rng_uniform(hh_meta.mIndex, 0, 31);

    // read the key and value at that location
    hh_meta.mKeyInTable = flow_tracker_stage1[hh_meta.mIndex];
    hh_meta.mCountInTable = packet_counter_stage1[hh_meta.mIndex];
    hh_meta.mValid = valid_bit_stage1[hh_meta.mIndex];

    // check if location is empty or has a differentkey in there
    hh_meta.mKeyInTable = (hh_meta.mValid == 0)? hh_meta.mKeyCarried : hh_meta.mKeyInTable;
    hh_meta.mDiff = (hh_meta.mValid == 0)? 0 : hh_meta.mKeyInTable - hh_meta.mKeyCarried;

    // generate another random value -- not sure if should go to 99 or 100
    modify_field_rng_uniform(hh_meta.mRand, 0, 100);

    // approximate log value
    hh_meta.mLog = ((hh_meta.mDiff == 0)? 100 :
        ((hh_meta.mCountInTable == 1)? 66 :
        ((hh_meta.mCountInTable <= 2)? 42 :
        ((hh_meta.mCountInTable <= 3)? 33 :
        ((hh_meta.mCountInTable <= 4)? 29 :
        ((hh_meta.mCountInTable <= 6)? 25 :
        ((hh_meta.mCountInTable <= 10)? 21 :
        ((hh_meta.mCountInTable <= 14)? 18 :
        ((hh_meta.mCountInTable <= 20)? 16 :
        ((hh_meta.mCountInTable <= 50)? 13 :
        ((hh_meta.mCountInTable <= 100)? 11 :
        ((hh_meta.mCountInTable <= 200)? 9 :
        ((hh_meta.mCountInTable <= 700)? 7 :
        ((hh_meta.mCountInTable <= 5000)? 6 :
        ((hh_meta.mCountInTable <= 100000)? 5 : 4)))))))))))))));

    // Indicates keep if negative, replace if >= 0
    hh_meta.mDiff = hh_meta.mLog - hh_meta.mRand;

    // update table
    flow_tracker_stage1[hh_meta.mIndex] = ((hh_meta.mDiff >= 0)?
        hh_meta.mKeyCarried : hh_meta.mKeyInTable);
    packet_counter_stage1[hh_meta.mIndex] = ((hh_meta.mDiff >= 0)?
        hh_meta.mCountInTable + 1 : hh_meta.mCountInTable);
    valid_bit_stage1[hh_meta.mIndex] = 1;

    // update metadata carried to the next table stage
    hh_meta.mKeyCarried = ((hh_meta.mDiff >= 0) ? 
        ((hh_meta.mValid == 0)? 0 : hh_meta.mKeyInTable) : hh_meta.mKeyCarried);
    hh_meta.mCountCarried = ((hh_meta.mDiff >= 0) ? hh_meta.mCountInTable : hh_meta.mCountCarried); 
}

table track_stage1 {
    actions { do_stage1; }
    size: 0;
}

/***************************************************************/
/********************** table stage 2 **************************/
/***************************************************************/

register flow_tracker_stage2 {
    width: 32;
    static: track_stage2;
    instance_count: 32;
}

register packet_counter_stage2 {
    width: 32;
    static: track_stage2;
    instance_count: 32;
}

register valid_bit_stage2 {
    width: 1;
    static: track_stage2;
    instance_count: 32;
}

action do_stage2(){
    // hash using my custom function 
    modify_field_with_hash_based_offset(hh_meta.mIndex, 0, stage2_hash,
    32);

    // read the key and value at that location
    hh_meta.mKeyInTable = flow_tracker_stage2[hh_meta.mIndex];
    hh_meta.mCountInTable = packet_counter_stage2[hh_meta.mIndex];
    hh_meta.mValid = valid_bit_stage2[hh_meta.mIndex];

    // check if location is empty or has a differentkey in there
    hh_meta.mKeyInTable = (hh_meta.mValid == 0)? hh_meta.mKeyCarried : hh_meta.mKeyInTable;
    hh_meta.mDiff = (hh_meta.mValid == 0)? 0 : hh_meta.mKeyInTable - hh_meta.mKeyCarried;

    // update table
    flow_tracker_stage2[hh_meta.mIndex] = ((hh_meta.mDiff == 0)?
    hh_meta.mKeyInTable : ((hh_meta.mCountInTable <
    hh_meta.mCountCarried) ? hh_meta.mKeyCarried :
    hh_meta.mKeyInTable));

    packet_counter_stage2[hh_meta.mIndex] = ((hh_meta.mDiff == 0)?
    hh_meta.mCountInTable + hh_meta.mCountCarried :
    ((hh_meta.mCountInTable < hh_meta.mCountCarried) ?
    hh_meta.mCountCarried : hh_meta.mCountInTable));

    valid_bit_stage2[hh_meta.mIndex] = ((hh_meta.mValid == 0) ?
    ((hh_meta.mKeyCarried == 0) ? (bit<1>)0 : 1) : (bit<1>)1);

    // update metadata carried to the next table stage
    hh_meta.mKeyCarried = ((hh_meta.mDiff == 0) ? 0:
    hh_meta.mKeyInTable);
    hh_meta.mCountCarried = ((hh_meta.mDiff == 0) ? 0:
    hh_meta.mCountInTable);  
}

table track_stage2 {
    actions { do_stage2; }
    size: 0;
}


// 0.05 = lowest bucket because one of our data sets highest is 19652, which equal 0.046
// for equation to equal 1, x=1.5849 or lower (so do below 1)
// <=1: 66
// 2: 42
// 3: 33
// 4: 29
// 5-6: 25
// 7-10: 21
// 11-14: 18
// 15-20: 16
// 21-50: 13
// 51-100: 11
// 101-200: 9
// 201-700: 7
// 701 - 5000: 6
// 5000 - 100000: 5
// 100001 and greater = 4

       