'''
Created on Nov 13, 2021

@author: piotr
'''

import numpy as np
from ObjectsDetectable.Classes import LicensePlateID, FaceID
from Detections.DetectionsMap import DetectionsMap_Cls
from Detections.Detection import BoundingBox_Cls
from Detector.MultiClassDetectors.MultiClassDetector import MultiClassDetector_Cls
from pathlib import Path
from NonPythonFiles.WorkersFiles.Detectors.UnderstandAI import UnderstandAI_weights_lpPath,\
    UnderstandAI_weights_facePath
from SW_Licensing.SW_License import License_Cls


class UnderstandAI_Cls(MultiClassDetector_Cls):
        
    @staticmethod
    def getClassesServiced():
        return {LicensePlateID, FaceID}
        
    @classmethod
    def allowOneInstanceServicingMultipleClassesAtATime(cls):
        return False
    
    @staticmethod
    def getName(): 
        return "UnderstandAI"
        
    @staticmethod
    def getDescription():
        return "AI based, origin: https://github.com/understand-ai/anonymizer"
    

    _weightsPaths_dict = {
        LicensePlateID  : UnderstandAI_weights_lpPath,
        FaceID          : UnderstandAI_weights_facePath
        }
    
    _detectionThreshold_dict = {
        LicensePlateID  : 0.3,    # Must be in [0.001, 1.0)
        FaceID          : 0.3     # Must be in [0.001, 1.0)
        }

    def __init__(self):
        '''
        Constructor
        '''
    
        import tensorflow as tf
        self._tensorflow = tf
        
        self._sessions_dict = {}
        self._detectionGraph_dict = {}
        
        self._detectionThreshold_dict = self._getDetectionThresholdsDict()
        
        MultiClassDetector_Cls.__init__(self)
    
    
    def _prepare(self):
        
        for classId in self.getClassesProcessedByInstance():
            weights_path = UnderstandAI_Cls._weightsPaths_dict[classId]
            weights_path = str((Path(__file__).parent / weights_path).absolute())
            self._sessions_dict[classId], self._detectionGraph_dict[classId] = self._constructDetectionGraphAndSession(weights_path)
    
    
    def _getDetectionThresholdsDict(self):
        "Pull data from class variable"
        
        output_dict = {}
        
        for classId in UnderstandAI_Cls._detectionThreshold_dict:
            detectionThreshold = UnderstandAI_Cls._detectionThreshold_dict[classId]
            
            assert detectionThreshold >= 0.001,  'Threshold can not be too close to "0".'
            assert detectionThreshold < 1,       'Threshold can not be euqal or greater than 1.'
            
            output_dict[classId] = detectionThreshold
        
        return output_dict
            
        
    def _constructDetectionGraphAndSession(self, weights_path):

        detection_graph = self._tensorflow.Graph()
        with detection_graph.as_default():
            od_graph_def = self._tensorflow.compat.v1.GraphDef()
            with self._tensorflow.compat.v1.gfile.GFile(weights_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                self._tensorflow.import_graph_def(od_graph_def, name='')

        conf = self._tensorflow.compat.v1.ConfigProto()
        session = self._tensorflow.compat.v1.Session(graph=detection_graph, config=conf)
        
        return session, detection_graph
    
    
    def _detect_class(self, nparray, classId):
        
        detectionsMap = DetectionsMap_Cls()
        
        try:
            session               =  self._sessions_dict[classId]
        except:
            raise
        
        detection_graph       =  self._detectionGraph_dict[classId]
        detection_threshold   =  self._detectionThreshold_dict[classId]
        
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        _, _, channels = nparray.shape
        assert channels == 3, f'Invalid number of channels: {channels}. ' \
                              f'Only images with three color channels are supported.'

        np_images = np.array([nparray])
        num_boxes, scores, boxes = session.run(
            [num_detections, detection_scores, detection_boxes],
            feed_dict={image_tensor: np_images})
        
        
        for i in range(int(num_boxes[0])):
            score = float(scores[0][i])
            if score < detection_threshold:
                continue
            
            y_min, x_min, y_max, x_max = map(float, boxes[0][i].tolist())
            
            detection = BoundingBox_Cls(class_ = classId,
                                        left = x_min,
                                        top = y_min,
                                        right = x_max,
                                        bottom = y_max)
    
            detectionsMap.addDetection(detection)
        
        return detectionsMap
    
    
    def _detectClasses(self, nparray, classIds):
        
        detectionsMap = DetectionsMap_Cls()
        
        for classId in classIds:
            
            detectionsMap += self._detect_class(nparray, classId)
        
        return detectionsMap
    
    
    def _detect(self, nparray):
        
        return self._detectClasses(nparray, self._detectableClasses)
        

    @staticmethod
    def getLicense():
        return License_Cls(
            type_ = "Apache 2.0 License",
            srcCodeLocation = "https://github.com/understand-ai/anonymizer",
            fullStatement = """Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS""")








