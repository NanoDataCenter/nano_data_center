extern crate bindgen;

use bindgen::callbacks::{ParseCallbacks, IntKind};

extern crate cc;

use std::env;
use std::path::PathBuf;

fn main() {

    println!("cargo:rerun-if-changed=src/CDeps");

    cc::Build::new()
        .file("src/CDeps/Redis/redismodule.c")
        .include("src/CDeps/Redis/include")
        .compile("libredismodule.a");

    cc::Build::new()
        .file("src/CDeps/SQLite/sqlite3.c")
        .include("src/CDeps/SQLite/include")
        .define("HAVE_USLEEP", Some("1"))
        .define("NDEBUG", Some("1"))
        .define("HAVE_FDATASYNC", Some("1"))
        .define("SQLITE_THREADSAFE", Some("1"))
        .define("SQLITE_ENABLE_JSON1", Some("1"))
        .define("SQLITE_ENABLE_FTS3", Some("1"))
        .define("SQLITE_ENABLE_FTS4", Some("1"))
        .define("SQLITE_ENABLE_FTS5", Some("1"))
        .define("SQLITE_ENABLE_RTREE", Some("1"))
        .compile("libsqlite3.a");

    #[derive(Debug)]
    struct SqliteTypeChooser;

    impl ParseCallbacks for SqliteTypeChooser {
        fn int_macro(&self,
                     _name: &str,
                     value: i64)
                     -> Option<IntKind> {
            if value >= i32::min_value() as i64 &&
               value <= i32::max_value() as i64 {
                Some(IntKind::I32)
            } else {
                None
            }
        }
    }

    let bindings =
        bindgen::Builder::default()
            .parse_callbacks(Box::new(SqliteTypeChooser))
            .header("sqlite_dependencies.h")
            .generate()
            .expect("Unable to generate bindings for SQLite");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings_sqlite.rs"))
        .expect("Couldn't write bindings for SQLite!");

    let bindings =
        bindgen::Builder::default()
            .parse_callbacks(Box::new(SqliteTypeChooser))
            .header("redis_dependencies.h")
            .generate()
            .expect("Unable to generate bindings for Redis");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings_redis.rs"))
        .expect("Couldn't write bindings for Redis!");
}
