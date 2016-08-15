// Copyright (c) 2016 University of Helsinki
// Copyright (c) 2016 Tino Didriksen <mail@tinodidriksen.com>
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
// See the file COPYING included with this distribution for more
// information.

#include "serialize.h"
#include <iostream>
#include <sstream>
#include <random>
#include <vector>

template<class T>
bool almost_equal(T x, T y, int ulp=2) {
	// NaN
	if (x != x && y != y) {
		return true;
	}

    return (x == y)
    	|| (std::abs(x-y) < std::numeric_limits<T>::epsilon() * std::abs(x+y) * ulp)
    	|| (std::abs(x-y) < std::numeric_limits<T>::min());
}


int main() {
	// Test all full bit patterns
	/*
	{
		std::stringstream ss;
		for (uint64_t i = 0, v = 0 ; i < 64 ; ++i) {
			v <<= 1;
			v |= 1;
			write(ss, v);
			write(ss, static_cast<int64_t>(v));
			write(ss, -static_cast<int64_t>(v));
		}
		for (uint64_t i = 0, v = 0 ; i < 64 ; ++i) {
			v <<= 1;
			v |= 1;
			std::cout << std::hex << v << " -> " << std::hex << read_u(ss) << std::endl;
			std::cout << std::hex << static_cast<int64_t>(v) << " -> " << std::hex << read_s(ss) << std::endl;
			std::cout << std::hex << -static_cast<int64_t>(v) << " -> " << std::hex << read_s(ss) << std::endl;
		}
	}
	//*/

	std::cout << std::dec;

	{
		std::cout << "Test random integer bit patterns:" << std::endl;
		/*
		std::fstream ss("/tmp/integer.bin", std::ios::binary | std::ios::in | std::ios::out | std::ios::trunc);
		/*/
		std::stringstream ss;
		//*/
		std::mt19937_64 rnd;

		std::vector<uint64_t> vals;
		// Test all full bit patterns
		for (uint64_t i = 0, v = 0 ; i < 64 ; ++i) {
			v <<= 1;
			v |= 1;
			vals.push_back(v);
			write(ss, v);
			write(ss, static_cast<int64_t>(v));
			write(ss, -static_cast<int64_t>(v));
		}

		// Test random bit patterns
		for (size_t i = 0 ; i < 1000000 ; ++i) {
			if (i % 1000 == 999) {
				std::cout << "Writing " << i << "\r";
			}
			vals.push_back(rnd());
			write(ss, vals.back());
			write(ss, static_cast<int64_t>(vals.back()));
			write(ss, -static_cast<int64_t>(vals.back()));
		}

		ss.seekg(0);

		for (size_t i = 0 ; i < vals.size() ; ++i) {
			if (i % 1000 == 999) {
				std::cout << "Reading " << i << "\r";
			}
			uint64_t v = read_u(ss);
			if (v != vals[i]) {
				std::cout << v << " != " << vals[i] << std::endl;
				return 1;
			}

			int64_t v2 = read_s(ss);
			if (v2 != static_cast<int64_t>(vals[i])) {
				std::cout << v2 << " != " << static_cast<int64_t>(vals[i]) << std::endl;
				return 2;
			}

			int64_t v3 = read_s(ss);
			if (v3 != -static_cast<int64_t>(vals[i])) {
				std::cout << v3 << " != " << -static_cast<int64_t>(vals[i]) << std::endl;
				return 3;
			}
		}
		std::cout << std::endl;
	}

	{
		std::cout << "Test random floating point bit patterns:" << std::endl;
		/*
		std::fstream ss("/tmp/float.bin", std::ios::binary | std::ios::in | std::ios::out | std::ios::trunc);
		/*/
		std::stringstream ss;
		//*/
		std::mt19937_64 rnd;
		std::uniform_real_distribution<long double> udr(std::numeric_limits<int64_t>::lowest(), std::numeric_limits<int64_t>::max());

		std::vector<long double> vals;
		long double corners[] = {
			std::numeric_limits<long double>::lowest(),
			std::numeric_limits<long double>::max(),
			std::numeric_limits<long double>::infinity(),
			std::numeric_limits<long double>::quiet_NaN(),
			0.0,
			1.0,
			-1.0,
			};
		for (auto v : corners) {
			vals.push_back(v);
			write(ss, vals.back());
			write(ss, static_cast<double>(vals.back()));
			write(ss, static_cast<float>(vals.back()));
		}

		for (size_t i = 0 ; i < 1000000 ; ++i) {
			if (i % 1000 == 999) {
				std::cout << "Writing " << i << "\r";
			}
			vals.push_back(udr(rnd));
			write(ss, vals.back());
			write(ss, static_cast<double>(vals.back()));
			write(ss, static_cast<float>(vals.back()));
		}

		ss.seekg(0);

		for (size_t i = 0 ; i < vals.size() ; ++i) {
			if (i % 1000 == 999) {
				std::cout << "Reading " << i << "\r";
			}
			long double v = 0;
			read(ss, v);
			if (!almost_equal(v, vals[i])) {
				std::cout << i << " long double " << v << " != " << vals[i] << std::endl;
				return 1;
			}

			double v2 = 0;
			read(ss, v2);
			if (!almost_equal(v2, static_cast<double>(vals[i]))) {
				std::cout << i << " double " << v2 << " != " << static_cast<double>(vals[i]) << std::endl;
				return 2;
			}

			float v3 = 0;
			read(ss, v3);
			if (!almost_equal(v3, static_cast<float>(vals[i]))) {
				std::cout << i << " float " << v3 << " != " << static_cast<float>(vals[i]) << std::endl;
				return 3;
			}
		}
		std::cout << std::endl;
	}
}
