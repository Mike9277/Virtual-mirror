/*
 * gVirtuS -- A GPGPU transparent virtualization component.
 *
 * Copyright (C) 2009-2010  The University of Napoli Parthenope at Naples.
 *
 * This file is part of gVirtuS.
 *
 * gVirtuS is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * gVirtuS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with gVirtuS; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Written by: Giuseppe Coviello <giuseppe.coviello@uniparthenope.it>,
 *             Department of Applied Science
 */

#include <mutex>
#include <unordered_map>

#include "CurandHandler.h"

using namespace std;
using namespace log4cplus;

using gvirtus::communicators::Buffer;
using gvirtus::communicators::Result;

static std::mutex generator_type_mutex;
static std::unordered_map<curandGenerator_t, bool> generator_is_host_map;

bool isHostGenerator(curandGenerator_t generator) {
    std::lock_guard<std::mutex> lock(generator_type_mutex);
    auto it = generator_is_host_map.find(generator);
    if (it != generator_is_host_map.end()) {
        return it->second;
    }
    return false;  // default to device generator
}

CURAND_ROUTINE_HANDLER(CreateGenerator) {
    // Create the generator, get handle
    curandGenerator_t generator;
    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    curandRngType_t gnrType = in->Get<curandRngType_t>();
    curandStatus_t cs = curandCreateGenerator(&generator, gnrType);

    if (cs == CURAND_STATUS_SUCCESS) {
        std::lock_guard<std::mutex> lock(generator_type_mutex);
        generator_is_host_map[generator] = false;  // device generator
    }

    out->Add<curandGenerator_t>(generator);
    return std::make_shared<Result>(cs, out);
}

CURAND_ROUTINE_HANDLER(CreateGeneratorHost) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("CreateGeneratorHost"));
    // Create host generator
    curandGenerator_t generator;
    std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
    curandRngType_t gnrType = in->Get<curandRngType_t>();
    curandStatus_t cs = curandCreateGeneratorHost(&generator, gnrType);

    if (cs == CURAND_STATUS_SUCCESS) {
        std::lock_guard<std::mutex> lock(generator_type_mutex);
        generator_is_host_map[generator] = true;  // host generator
    }

    out->Add<curandGenerator_t>(generator);
    return std::make_shared<Result>(cs, out);
}

CURAND_ROUTINE_HANDLER(SetPseudoRandomGeneratorSeed) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("SetPseudoRandomGeneratorSeed"));

    curandGenerator_t generator = in->Get<curandGenerator_t>();
    unsigned long long seed = in->Get<unsigned long long>();

    curandStatus_t cs = curandSetPseudoRandomGeneratorSeed(generator, seed);
    return std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(SetGeneratorOffset) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("SetGeneratorOffset"));

    curandGenerator_t generator = in->Get<curandGenerator_t>();
    unsigned long long offset = in->Get<unsigned long long>();

    LOG4CPLUS_DEBUG(logger, "Generator pointer: " << generator << ", offset: " << offset);

    curandStatus_t cs = curandSetGeneratorOffset(generator, offset);
    return std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(SetQuasiRandomGeneratorDimensions) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("SetQuasiRandomGeneratorDimensions"));

    curandGenerator_t generator = in->Get<curandGenerator_t>();
    unsigned int num_dimensions = in->Get<unsigned int>();

    LOG4CPLUS_DEBUG(logger, "Generator pointer: " << generator << ", num_dimensions: " << num_dimensions);

    curandStatus_t cs = curandSetQuasiRandomGeneratorDimensions(generator, num_dimensions);
    return std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(Generate) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("Generate"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    unsigned int* outputPtr = isHost
            ? out->Delegate<unsigned int>(num)
            : in->Get<unsigned int*>();

    cs = curandGenerate(generator, outputPtr, num);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GenerateLongLong) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateLongLoong"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    unsigned long long* outputPtr = isHost
            ? out->Delegate<unsigned long long>(num)
            : in->Get<unsigned long long*>();
            
    cs = curandGenerateLongLong(generator, outputPtr, num);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GenerateUniform) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateUniform"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    float* outputPtr = isHost ? out->Delegate<float>(num) : in->Get<float*>();

    cs = curandGenerateUniform(generator, outputPtr, num);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GenerateNormal) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateNormal"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    float mean = in->Get<float>();
    float stddev = in->Get<float>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    float* outputPtr = isHost ? out->Delegate<float>(num) : in->Get<float*>();

    cs = curandGenerateNormal(generator, outputPtr, num, mean, stddev);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

// alternative implementation of GenerateNormal without using Delegate
// CURAND_ROUTINE_HANDLER(GenerateNormal) {
//     Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateNormal"));

//     curandStatus_t cs;
//     curandGenerator_t generator = in->Get<curandGenerator_t>();
//     size_t num = in->Get<size_t>();
//     float mean = in->Get<float>();
//     float stddev = in->Get<float>();
//     bool isHost = isHostGenerator(generator);
//     float* outputPtr = isHost ? in->Get<float>(num) : in->Get<float*>();

//     cs = curandGenerateNormal(generator, outputPtr, num, mean, stddev);
//     if (isHost) {
//         std::shared_ptr<Buffer> out = std::make_shared<Buffer>();
//         out->Add<float>(outputPtr, num);
//         return std::make_shared<Result>(cs, out);
//     }
//     return std::make_shared<Result>(cs);
// }

CURAND_ROUTINE_HANDLER(GenerateLogNormal) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateLogNormal"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    float mean = in->Get<float>();
    float stddev = in->Get<float>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    float* outputPtr = isHost ? out->Delegate<float>(num) : in->Get<float*>();

    cs = curandGenerateLogNormal(generator, outputPtr, num, mean, stddev);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GeneratePoisson) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GeneratePoisson"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    double lambda = in->Get<double>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    unsigned int* outputPtr = isHost ? out->Delegate<unsigned int>(num) : in->Get<unsigned int*>();

    cs = curandGeneratePoisson(generator, outputPtr, num, lambda);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GenerateUniformDouble) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateUniformDouble"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    double* outputPtr = isHost ? out->Delegate<double>(num) : in->Get<double*>();

    cs = curandGenerateUniformDouble(generator, outputPtr, num);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GenerateNormalDouble) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateNormalDouble"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    size_t num = in->Get<size_t>();
    double mean = in->Get<double>();
    double stddev = in->Get<double>();
    bool isHost = isHostGenerator(generator);
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    double* outputPtr = isHost ? out->Delegate<double>(num) : in->Get<double*>();

    cs = curandGenerateNormalDouble(generator, outputPtr, num, mean, stddev);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(GenerateLogNormalDouble) {
    Logger logger = Logger::getInstance(LOG4CPLUS_TEXT("GenerateLogNormalDouble"));

    curandStatus_t cs;
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    bool isHost = isHostGenerator(generator);
    size_t num = in->Get<size_t>();
    double mean = in->Get<double>();
    double stddev = in->Get<double>();
    std::shared_ptr<Buffer> out = isHost ? std::make_shared<Buffer>() : nullptr;
    double* outputPtr = isHost ? out->Delegate<double>(num) : in->Get<double*>();

    cs = curandGenerateLogNormalDouble(generator, outputPtr, num, mean, stddev);
    return isHost ? std::make_shared<Result>(cs, out) : std::make_shared<Result>(cs);
}

CURAND_ROUTINE_HANDLER(DestroyGenerator) {
    curandGenerator_t generator = in->Get<curandGenerator_t>();
    curandStatus_t cs = curandDestroyGenerator(generator);

    if (cs == CURAND_STATUS_SUCCESS) {
        std::lock_guard<std::mutex> lock(generator_type_mutex);
        generator_is_host_map.erase(generator);
    }

    return std::make_shared<Result>(cs);
}