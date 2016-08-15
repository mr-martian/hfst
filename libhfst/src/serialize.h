// Copyright (c) 2016 University of Helsinki
// Copyright (c) 2016 Tino Didriksen <mail@tinodidriksen.com>
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
// See the file COPYING included with this distribution for more
// information.

#ifndef h528875857d20d46c40431bf8afad57e89259ce78_SERIALIZE_HPP_
#define h528875857d20d46c40431bf8afad57e89259ce78_SERIALIZE_HPP_

#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <limits>
#include <stdint.h>

// Writing
template<typename T>
inline void write(T& os, const char *buf, size_t n) {
	for (size_t i=0 ; i<n ; ++i) {
		os.write(buf[i]);
	}
}

inline void write(std::ostream& os, const char *buf, size_t n) {
	os.write(buf, n);
}

inline void write(std::ofstream& os, const char *buf, size_t n) {
	os.write(buf, n);
}

inline void write(std::fstream& os, const char *buf, size_t n) {
	os.write(buf, n);
}

inline void write(std::ostringstream& os, const char *buf, size_t n) {
	os.write(buf, n);
}

inline void write(std::stringstream& os, const char *buf, size_t n) {
	os.write(buf, n);
}

inline void write(FILE *os, const char *buf, size_t n) {
	(void)fwrite(buf, 1, n, os);
}

// Unsigned base case and variants
template<typename T>
#ifdef __GNUG__
__attribute__((optimize("unroll-loops")))
#endif
inline void write(T& os, uint64_t v) {
	uint8_t bytes = 0;
	for (uint8_t i = 8 ; i > 0 ; --i) {
		uint64_t k = (1ull << (7ull - (i - 1) + 8ull * (i - 1)));
		if (v >= k) {
			bytes = i;
			break;
		}
	}

	uint8_t buf[9] = { static_cast<uint8_t>(~0u << (8 - bytes)) };
	for (uint8_t i = 0 ; i < bytes ; ++i) {
		uint8_t val = v & 0xffu;
		buf[i + 1] = val;
		v >>= 8;
	}
	if (bytes < 8) {
		buf[0] |= v;
	}

	write(os, reinterpret_cast<const char*>(&buf[0]), bytes + 1);
}

template<typename T>
inline void write(T& os, uint32_t v) {
	write(os, static_cast<uint64_t>(v));
}

template<typename T>
inline void write(T& os, uint16_t v) {
	write(os, static_cast<uint64_t>(v));
}

template<typename T>
inline void write(T& os, uint8_t v) {
	write(os, static_cast<uint64_t>(v));
}

// Signed variants
template<typename T>
inline void write(T& os, int64_t v) {
	write(os, (static_cast<uint64_t>(v) << 1) ^ (v >> 63));
}

template<typename T>
inline void write(T& os, int32_t v) {
	write(os, static_cast<int64_t>(v));
}

template<typename T>
inline void write(T& os, int16_t v) {
	write(os, static_cast<int64_t>(v));
}

template<typename T>
inline void write(T& os, int8_t v) {
	write(os, static_cast<int64_t>(v));
}

// Floating point variants
template<typename T>
inline void write(T& os, long double v) {
	// Special case: Infinity
	if (v == std::numeric_limits<long double>::infinity()) {
		write(os, std::numeric_limits<int64_t>::max());
		return;
	}
	// Special case: Negative infinity
	if (v == -std::numeric_limits<long double>::infinity()) {
		write(os, std::numeric_limits<int64_t>::max()-1);
		return;
	}
	// Special case: NaN
	if (v != v) {
		write(os, std::numeric_limits<int64_t>::max()-2);
		return;
	}
	int e = 0;
	int64_t m = static_cast<int64_t>((std::numeric_limits<int64_t>::max()-3) * std::frexp(v, &e));
	write(os, m);
	write(os, static_cast<int64_t>(e));
}

template<typename T>
inline void write(T& os, double v) {
	write(os, static_cast<long double>(v));
}

template<typename T>
inline void write(T& os, float v) {
	write(os, static_cast<long double>(v));
}

// Boolean variant
template<typename T>
inline void write(T& os, bool v) {
	write(os, static_cast<uint64_t>(v));
}

// Reading
template<typename T>
inline void read(T& is, char *buf, size_t n) {
	for (size_t i=0 ; i<n ; ++i) {
		buf[i] = is.stream_get();
	}
}

inline void read(std::istream& is, char *buf, size_t n) {
	is.read(buf, n);
}

inline void read(std::ifstream& is, char *buf, size_t n) {
	is.read(buf, n);
}

inline void read(std::fstream& is, char *buf, size_t n) {
	is.read(buf, n);
}

inline void read(std::istringstream& is, char *buf, size_t n) {
	is.read(buf, n);
}

inline void read(std::stringstream& is, char *buf, size_t n) {
	is.read(buf, n);
}

inline void read(FILE *is, char *buf, size_t n) {
	(void)fread(buf, 1, n, is);
}

// Unsigned base case and variants
template<typename T>
#ifdef __GNUG__
__attribute__((optimize("unroll-loops")))
#endif
inline uint64_t read_u(T& is) {
	uint64_t v = 0;

	uint8_t head;
	read(is, reinterpret_cast<char*>(&head), 1);
	uint8_t bytes = 0;
	for (uint8_t i = 8 ; i > 0 ; --i) {
		uint8_t mask = (~0u << (8 - i));
		if ((head & mask) == mask) {
			bytes = i;
			break;
		}
	}

	if (bytes < 8) {
		v |= head & ~(~0 << (7 - bytes));
	}

	uint8_t buf[8] = {};
	read(is, reinterpret_cast<char*>(&buf), bytes);
	for (uint8_t i = bytes ; i > 0 ; --i) {
		v <<= 8;
		v |= buf[i - 1];
	}

	return v;
}

template<typename T>
inline uint64_t read(T& is, uint64_t& v) {
	v = read_u(is);
	return v;
}

template<typename T>
inline uint32_t read(T& is, uint32_t& v) {
	v = static_cast<uint32_t>(read_u(is));
	return v;
}

template<typename T>
inline uint16_t read(T& is, uint16_t& v) {
	v = static_cast<uint16_t>(read_u(is));
	return v;
}

template<typename T>
inline uint8_t read(T& is, uint8_t& v) {
	v = static_cast<uint8_t>(read_u(is));
	return v;
}

// Signed variants
template<typename T>
inline int64_t read_s(T& is) {
	uint64_t v = read_u(is);
	return (static_cast<int64_t>(v >> 1) ^ static_cast<int64_t>(-(v & 1)));
}

template<typename T>
inline int64_t read(T& is, int64_t& v) {
	v = read_s(is);
	return v;
}

template<typename T>
inline int32_t read(T& is, int32_t& v) {
	v = static_cast<int32_t>(read_s(is));
	return v;
}

template<typename T>
inline int16_t read(T& is, int16_t& v) {
	v = static_cast<int16_t>(read_s(is));
	return v;
}

template<typename T>
inline int8_t read(T& is, int8_t& v) {
	v = static_cast<int8_t>(read_s(is));
	return v;
}

// Floating point variants
template<typename T>
inline long double read(T& is, long double& v) {
	int64_t u = read_s(is);
	if (u == std::numeric_limits<int64_t>::max()) {
		v = std::numeric_limits<long double>::infinity();
		return v;
	}
	if (u == std::numeric_limits<int64_t>::max()-1) {
		v = -std::numeric_limits<long double>::infinity();
		return v;
	}
	if (u == std::numeric_limits<int64_t>::max()-2) {
		v = std::numeric_limits<long double>::quiet_NaN();
		return v;
	}

	long double m = static_cast<long double>(u) / (std::numeric_limits<int64_t>::max()-3);
	int64_t e = read_s(is);
	v = std::ldexp(m, static_cast<int>(e));
	return v;
}

template<typename T>
inline double read(T& is, double& v) {
	long double u = 0;
	read(is, u);
	v = static_cast<double>(u);
	return v;
}

template<typename T>
inline float read(T& is, float& v) {
	long double u = 0;
	read(is, u);
	v = static_cast<float>(u);
	return v;
}

// Boolean variants
template<typename T>
inline bool read_b(T& is) {
	uint64_t v = read_u(is);
	return (v != 0);
}

template<typename T>
inline bool read(T& is, bool& v) {
	v = read_b(is);
	return v;
}

#endif
